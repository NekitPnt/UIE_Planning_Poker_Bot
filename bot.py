from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN
from comanager import Err, params, VOTING_SEP, MARKS, rerun, open_cards, score_action, \
    clear_ftr, help_ftr, task_ftr, report_ftr, next_ftr, vote_cb, service_cb, TASKS_SEP
from classes import RoomTemp, TaskTemp, Ftr
from utils import replace_user_mark, get_score_inst, get_username, clear_task_text, send_task, report_generator

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
users_data = {}


async def create_or_clear_room(msg: types.Message):
    username = await get_username(msg)
    users_data.update({msg.chat.id: RoomTemp(msg.chat.id, msg.from_user.id, username, [])})


async def send_report(msg: types.Message):
    if msg.chat.id in users_data:
        room_data = users_data[msg.chat.id]
        if room_data.tasks:
            # генерация отчета по сессии
            report = await report_generator(room_data)
            await msg.answer(report_ftr.text)
            await bot.send_document(msg.chat.id, report)
        else:
            await msg.answer(Err.empty_queue)
    else:
        await msg.answer(Err.empty_queue)


@dp.message_handler(commands=help_ftr.commands)
async def help_comm(msg: types.Message):
    await msg.answer(Ftr.generate_help())


@dp.message_handler(commands=clear_ftr.commands)
async def clear_tasks_com(msg: types.Message):
    if msg.chat.id in users_data and users_data[msg.chat.id].tasks:
        if msg.from_user.id == users_data[msg.chat.id].onwer_id:
            await create_or_clear_room(msg)
            await msg.answer(clear_ftr.text)
        else:
            await msg.answer(Err.denied)
    else:
        await msg.answer(Err.empty_queue)


@dp.message_handler(commands=task_ftr.commands)
async def new_tasks_comm(msg: types.Message):
    if msg.text:
        # creating room
        if msg.chat.id not in users_data:
            await create_or_clear_room(msg)
        room_data = users_data[msg.chat.id]
        # set tasks to room
        tasks = msg.get_args().split(TASKS_SEP)
        for task in tasks:
            room_data.tasks.append({})
            for param in params:
                room_data.tasks[-1].update({param.key: TaskTemp(task, param)})
        # send first task to vote
        await send_task(msg, room_data)
    else:
        await msg.answer(Err.empty_start)


@dp.message_handler(commands=report_ftr.commands)
async def report_com(msg: types.Message):
    await send_report(msg)


@dp.message_handler(commands=next_ftr.commands)
async def next_task_com(msg: types.Message):
    if msg.chat.id in users_data and users_data[msg.chat.id].tasks:
        if msg.from_user.id == users_data[msg.chat.id].onwer_id:
            room_data = users_data[msg.chat.id]
            if room_data.current_task < len(room_data.tasks):
                await send_task(msg, room_data)
            else:
                await send_report(msg)
        else:
            await msg.answer(Err.denied)
    else:
        await msg.answer(Err.empty_queue)


@dp.callback_query_handler(vote_cb.filter(action=[score_action]))
async def voting_com(call: types.CallbackQuery, callback_data: dict):
    username = await get_username(call)
    # update vote
    param_key = callback_data["p"]
    task_id = int(callback_data["id"])
    room_data = users_data[call.message.chat.id]
    task = room_data.tasks[task_id][param_key]
    if not task.opened:
        task.score.update({username: callback_data["v"]})
        # update msg text
        new_text = call.message.text
        new_mark = MARKS[0]
        if VOTING_SEP not in new_text:
            new_text += f'\n\n{VOTING_SEP}'
        if username not in new_text.split(VOTING_SEP)[-1]:
            new_text += f"\n{new_mark} {username}"
        else:
            new_text = await replace_user_mark(new_text, username)
        await call.message.edit_text(new_text, reply_markup=call.message.reply_markup)
    else:
        await call.answer(text=Err.cant_vote, show_alert=True)
    await call.answer()


@dp.callback_query_handler(service_cb.filter(action=[open_cards.callback]))
async def open_com(call: types.CallbackQuery, callback_data: dict):
    if call.from_user.id != users_data[call.message.chat.id].onwer_id:
        await call.answer(text=Err.denied, show_alert=True)
    else:
        # get task
        param_key = callback_data["p"]
        task_id = int(callback_data["id"])
        room_data = users_data[call.message.chat.id]
        task = room_data.tasks[task_id][param_key]
        # update msg text if not opened
        if not task.opened:
            text = call.message.text
            if VOTING_SEP not in text:
                await call.answer(text=Err.no_votes, show_alert=True)
            else:
                task.opened = True
                header = text.split(VOTING_SEP)[0]
                footer = '\n'.join(f'{get_score_inst(v).label} {u}' for u, v in task.score.items())
                new_text = f'{header}{VOTING_SEP}\n{footer}'
                await call.message.edit_text(new_text, reply_markup=call.message.reply_markup)
    await call.answer()


@dp.callback_query_handler(service_cb.filter(action=[rerun.callback]))
async def restart_com(call: types.CallbackQuery, callback_data: dict):
    if call.from_user.id != users_data[call.message.chat.id].onwer_id:
        await call.answer(text=Err.denied, show_alert=True)
    else:
        param_key = callback_data["p"]
        task_id = int(callback_data["id"])
        room_data = users_data[call.message.chat.id]
        task = room_data.tasks[task_id][param_key]
        new_text = await clear_task_text(task, room_data)
        task.opened = False
        # if task got votes
        if task.score:
            task.score = {}
            await call.message.edit_text(new_text, reply_markup=call.message.reply_markup)
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp)
