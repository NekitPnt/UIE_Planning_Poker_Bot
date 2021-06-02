from dataclasses import dataclass
from itertools import chain

from aiogram.utils.callback_data import CallbackData

from classes import Param, Score, ServiceButtons, Ftr


VOTING_SEP = "Проголосовали:"
MARKS = "♥♦♠♣"
TASKS_SEP = ","


@dataclass
class Err:
    empty_start = "empty task(s)"
    denied = "Доступно только владельцу задач"
    empty_queue = "Очередь задач пуста"
    no_votes = "Еще никто не проголосовал!"
    cant_vote = "Вы не можете голосовать после того как карты были открыты"


# базовые параметры
time_param = Param("time", "срочность", "срочности")
hard_param = Param("hard", "легкость", "легкости", 0.2)
important_param = Param("important", "важность", "важности")
# кастомные параметры
value_param = Param("value", "ценность", "ценности")
sc_param = Param("science", "научная новизна", "научной новизне", 0.4)
act_param = Param("actuality", "актуальность", "актуальности", 0.4)

params = [time_param, hard_param, important_param]
params_descr = ', '.join(p.name for p in params)
# расстановка весов в зависимости от количества параметров оценки
no_w = []
with_w = []
for param in params:
    if param.weight:
        with_w.append(param)
    else:
        no_w.append(param)
    # if with_w and sum([p.weight for p in with_w]) > 1:
if no_w:
    no_w_sum = (1 - sum([p.weight for p in with_w])) * 100 if with_w else 100
    for par in no_w:
        par.weight = no_w_sum / len(no_w)

help_ftr = Ftr("help text", ["help", "start"], "Список команд и помощь")
task_ftr = Ftr("Оценка задачи по {0}:\n{1}\n\nВладелец: {2}", ["tasks"],
               f"[задачa(и)] Добавление задачи в очередь оценки. Чтобы добавить несколько задач разделите их запятой. "
               f"Оценка каждой задачи проводится по следующим параметрам: {params_descr}")
clear_ftr = Ftr("Очередь задач очищена", ["clear"], "Очистить очередь задач")
report_ftr = Ftr("Отчет по сессии:", ["report"], "Сгенерировать отчет по всей текущей очереди задач")
next_ftr = Ftr("", ["next"], "Переход к следующей задаче для оценки")

scr1 = Score("1", 1)
scr2 = Score("2", 2)
scr3 = Score("3", 3)
scr5 = Score("5", 5)
scr8 = Score("8", 8)
scr13 = Score("13", 13)
scr20 = Score("20", 20)
scr40 = Score("40", 40)
scr0 = Score("?", 0)
scr_break = Score("☕", -1)
score_action = "vote"

scores_kb = [
    [scr1, scr2, scr3, scr5, scr8],
    [scr13, scr20, scr40, scr0, scr_break]
]
all_scores = (list(chain(*scores_kb)))

rerun = ServiceButtons("Рестарт", "restart")
open_cards = ServiceButtons("Открыть карты", "open_cards")

service_kb = [rerun, open_cards]

vote_cb = CallbackData("cb", "id", "action", "p", "v")
service_cb = CallbackData("cb", "id", "action", "p")
