import csv
from typing import List

from aiogram import types

from comanager import VOTING_SEP, all_scores, scores_kb, service_kb, MARKS, score_action, task_ftr, vote_cb, service_cb, \
    params


async def replace_user_mark(text: str, username: str):
    text_arr = text.split(VOTING_SEP)
    voters = text_arr[-1].split('\n')
    for line in range(len(voters)):
        if username in voters[line]:
            old_mark = voters[line].split()[0]
            new_mark = MARKS[(MARKS.index(old_mark) + 1) % len(MARKS)]
            voters[line] = f"{new_mark} {username}"
    voters = '\n'.join(i for i in voters)
    return f'{text_arr[0]}{VOTING_SEP}{voters}'


def get_score_inst(val: float):
    for i in all_scores:
        if i.value == int(val):
            return i


async def get_username(msg: [types.Message, types.CallbackQuery]):
    if msg.from_user.first_name:
        return f"@{msg.from_user.username} ({msg.from_user.first_name})"
    return f"@{msg.from_user.username}"


async def clear_task_text(task, room_data) -> str:
    return task_ftr.text.format(task.param.name2, task.name, room_data.onwer_name)


async def send_task(msg: types.Message, room_data):
    task_id = room_data.current_task
    for param_key, task in room_data.tasks[task_id].items():
        text = await clear_task_text(task, room_data)
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        for button_row in scores_kb:
            keyboard.add(*[types.InlineKeyboardButton(text=btn.label, callback_data=vote_cb.new(
                id=task_id, action=score_action, p=param_key, v=btn.value)) for btn in button_row])
        keyboard.add(*[types.InlineKeyboardButton(text=btn.label, callback_data=service_cb.new(
            id=task_id, action=btn.callback, p=param_key)) for btn in service_kb])
        await msg.answer(text, reply_markup=keyboard)
    room_data.current_task += 1


async def report_generator(room_data):
    result = []
    for task in room_data.tasks:
        res = []
        task_name = "None"
        for param_key, p_task in task.items():
            task_name = p_task.name
            res.append(round(sum([int(v) * p_task.param.weight for u, v in p_task.score.items()]) // len(p_task.score)))
        res = [task_name, *res, sum(res)]
        result.append(res)
    result = sorted(result, key=lambda x: x[-1], reverse=True)
    report_data = [[''] + [p.name for p in params] + ['total']] + result
    file = await report_file_creator('report.csv', report_data)
    return open('report.csv', 'rb')


async def report_file_creator(path: str, data: List[list]):
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)
