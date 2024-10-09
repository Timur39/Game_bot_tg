import random
import time

import telebot
from telebot import types

from secret_data import token

bot = telebot.TeleBot(token)

coins = 100
difficulty = 'easy'
quiz_counter = 0
win_counter = 0


def goose_number(user_number: int, computer_number: int):
    if user_number > computer_number:
        return f'Вы ввели число больше загаданного'
    elif user_number < computer_number:
        return f'Вы ввели число меньше загаданного'
    else:
        return 'победа'


def tic_tac_toe_check_win(gameboard: list[str], krestik_or_nolik: str):
    if gameboard[0] == krestik_or_nolik and gameboard[1] == krestik_or_nolik and gameboard[2] == krestik_or_nolik:
        return True
    elif gameboard[0] == krestik_or_nolik and gameboard[3] == krestik_or_nolik and gameboard[6] == krestik_or_nolik:
        return True
    elif gameboard[3] == krestik_or_nolik and gameboard[4] == krestik_or_nolik and gameboard[5] == krestik_or_nolik:
        return True
    elif gameboard[6] == krestik_or_nolik and gameboard[7] == krestik_or_nolik and gameboard[8] == krestik_or_nolik:
        return True
    elif gameboard[1] == krestik_or_nolik and gameboard[4] == krestik_or_nolik and gameboard[7] == krestik_or_nolik:
        return True
    elif gameboard[2] == krestik_or_nolik and gameboard[5] == krestik_or_nolik and gameboard[8] == krestik_or_nolik:
        return True
    elif gameboard[0] == krestik_or_nolik and gameboard[4] == krestik_or_nolik and gameboard[8] == krestik_or_nolik:
        return True
    elif gameboard[2] == krestik_or_nolik and gameboard[4] == krestik_or_nolik and gameboard[6] == krestik_or_nolik:
        return True
    else:
        return False


def rock_paper_scissors_check(user_answer, computer_answer):
    if user_answer == computer_answer:
        return 'Ничья'
    elif user_answer == 'камень' and computer_answer == 'ножницы':
        return 'Ты победил'
    elif user_answer == 'ножницы' and computer_answer == 'бумага':
        return 'Ты победил'
    elif user_answer == 'бумага' and computer_answer == 'камень':
        return 'Ты победил'
    else:
        return 'Ты проиграл'


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton('Угадай число(бесплатно)')
    item2 = types.KeyboardButton('Камень ножницы бумага(15 монет)')
    item3 = types.KeyboardButton('Крестики нолики(25 монет)')
    item4 = types.KeyboardButton('Викторина(50 монет)')
    item5 = types.KeyboardButton('Финальная игра(100 монет)')
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id,
                     f'Привет, я бот-помощник.\nТвоя задача пройти все игры.\nНо не все так просто их нужно разблокировать за монеты. Монеты дается за прохождение игр.',
                     reply_markup=markup)
    bot.register_next_step_handler(message, second_step_start_handler)


def second_step_start_handler(message):
    global quiz_counter, win_counter
    markup = types.ReplyKeyboardRemove()
    if message.text == 'Угадай число(бесплатно)':
        bot.send_message(message.chat.id,
                         f'Вы выбрали игру: Угадай число\nВы должны угадать число от 1 до 100, которое я загадаю\nЯ буду давать вам подсказки\nУровень сложности: {difficulty}',
                         reply_markup=markup)
        computer_number = random.randint(1, 100)
        counter = 1
        bot.register_next_step_handler(message, game_goose_number, computer_number, counter)
    elif message.text == 'Крестики нолики(25 монет)' and coins >= 25:
        bot.send_message(message.chat.id,
                         f'Вы выбрали игру: Крестики нолики\nВы должны победить меня, расположив крестики или нолики в ряд\nИграем до первой победы',
                         reply_markup=markup)
        computer_step = random.randint(0, 9)
        reversed_lst = ['❌', '⭕️']
        reversed_lst.reverse()
        krestik_or_nolik = random.choice([['❌', '⭕️'], reversed_lst])
        game_tic_tac_toe(message, computer_step, krestik_or_nolik)
    elif message.text == 'Камень ножницы бумага(15 монет)' and coins >= 15:
        bot.send_message(message.chat.id,
                         f'Вы выбрали игру: Камень ножницы бумага\nВы должны победить меня\nУровень сложности: {difficulty}\nВведите 🪨(камень) или ✂️(ножницы) или 📄(бумага)',
                         reply_markup=markup)
        win_counter = 0
        lose_counter = 0
        bot.register_next_step_handler(message, rock_paper_scissors, win_counter, lose_counter)
    elif message.text == 'Викторина(50 монет)' and coins >= 50:
        bot.send_message(message.chat.id,
                         f'Вы выбрали игру: Викторина\nВы должны ответить все на вопросы\nУровень сложности: {difficulty}',
                         reply_markup=markup)
        win_counter = 0
        quiz_counter = 0
        questions = {}
        with open('questions.txt', mode='r', encoding='utf-8') as file:
            file = file.readlines()
            for line in file:
                question, answer = line.split(';')
                questions[question] = answer.replace('\n', '').split(':')
        questions = list(questions.items())
        random.shuffle(questions)
        questions_shuffled = dict(questions)
        game_quiz(message, questions_shuffled)
    elif message.text == 'Финальная игра(100 монет)' and coins >= 100:
        pass
    else:
        bot.send_message(message.chat.id, f'Вам не хватает монет или такой игры не существует. Выберите другую игру.')
        bot.register_next_step_handler(message, second_step_start_handler)


def game_goose_number(message, computer_number: int, counter: int):
    global coins
    if not message.text.isdigit():
        bot.send_message(message.chat.id, f'Вы ввели не число')
        bot.register_next_step_handler(message, game_goose_number, computer_number, counter)
    elif int(message.text) > 100:
        bot.send_message(message.chat.id, f'Вы ввели число больше 100')
        bot.register_next_step_handler(message, game_goose_number, computer_number, counter)
    elif int(message.text) < 1:
        bot.send_message(message.chat.id, f'Вы ввели число меньше 1')
        bot.register_next_step_handler(message, game_goose_number, computer_number, counter)
    else:
        steps = 8
        if difficulty == 'normal':
            steps = 6
        elif difficulty == 'hard':
            steps = 5
        answer = goose_number(int(message.text), computer_number)
        if answer == 'победа':
            coins += 5
            bot.send_message(message.chat.id, f'Вы победили это число: {computer_number}\n+5 монет')
            bot.send_message(message.chat.id,
                             f'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')
            return
        bot.send_message(message.chat.id, f'{answer}')
        if counter < steps:
            counter += 1
            if int(message.text) == computer_number:
                bot.send_message(message.chat.id,
                                 f'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')
                return
            else:
                bot.register_next_step_handler(message, game_goose_number, computer_number, counter)
        else:
            bot.send_message(message.chat.id, f'Вы проиграли. Я загадал число: {computer_number}')
            bot.send_message(message.chat.id,
                             f'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')


def game_tic_tac_toe(message, computer_step: int, krestik_or_nolik: list[str],
                     first_step: str = random.choice(['computer', 'user']), gameboard=None):
    global coins
    if gameboard is None:
        gameboard = ['⬜', '⬜', '⬜',
                     '⬜', '⬜', '⬜',
                     '⬜', '⬜', '⬜']
    user = krestik_or_nolik[0]
    computer = krestik_or_nolik[1]
    if tic_tac_toe_check_win(gameboard, krestik_or_nolik[0]):
        coins += 20
        bot.send_message(message.chat.id, f'Вы победили!\n+20 монет')
        bot.send_message(message.chat.id,
                         f'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')
        return
    elif tic_tac_toe_check_win(gameboard, krestik_or_nolik[1]):
        bot.send_message(message.chat.id, f'Вы проиграли!')
        bot.send_message(message.chat.id,
                         f'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')
        return
    elif not '⬜' in gameboard:
        bot.send_message(message.chat.id, 'Игра закончена в ничью!')
        bot.send_message(message.chat.id,
                         'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова')
        return
    if first_step == 'computer':
        time.sleep(1)
        for i in range(len(gameboard)):
            if gameboard[computer_step - 1] == '⬜':
                gameboard[computer_step - 1] = computer
                gameboard2 = gameboard[::]
                gameboard2.insert(3, '\n')
                gameboard2.insert(7, '\n')
                gameboard2.insert(11, '\n')
                bot.send_message(message.chat.id, 'Ход компьютера')
                bot.send_message(message.chat.id, ''.join(gameboard2))
                first_step = 'user'
                game_tic_tac_toe(message, computer_step, krestik_or_nolik, first_step, gameboard)
                break
            else:
                computer_step = i
    else:
        bot.send_message(message.chat.id, f'Ваш ход\nВы {user}\nДля хода напишите число от 1 до 9')
        bot.register_next_step_handler(message, game_tic_tac_toe_user_step, computer_step, krestik_or_nolik, first_step,
                                       gameboard)


def game_tic_tac_toe_user_step(message, computer_step, krestik_or_nolik, first_step, gameboard):
    if message.text.isdigit():
        if int(message.text) in range(1, 10):
            if gameboard[int(message.text) - 1] == '⬜':
                gameboard[int(message.text) - 1] = krestik_or_nolik[0]
                gameboard2 = gameboard[::]
                gameboard2.insert(3, '\n')
                gameboard2.insert(7, '\n')
                gameboard2.insert(11, '\n')
                bot.send_message(message.chat.id, f'{''.join(gameboard2)}')
                first_step = 'computer'
                game_tic_tac_toe(message, computer_step, krestik_or_nolik, first_step, gameboard)
            else:
                bot.send_message(message.chat.id,
                                 f'Вы ввели неверное значение или эта клетка уже перекрыта. Попробуйте снова')
                bot.register_next_step_handler(message, game_tic_tac_toe, computer_step, krestik_or_nolik, first_step,
                                               gameboard)


def rock_paper_scissors(message, win_counter: int, lose_counter: int,
                        computer_step: list[str] = random.choice(['камень', 'ножницы', 'бумага'])):
    global coins
    win = 3
    if difficulty == 'normal':
        win = 3
    elif difficulty == 'hard':
        win = 5
    user_answer = message.text.lower()
    words_to_emoji = {'камень': '🪨',
                      'ножницы': '✂️',
                      'бумага': '📄'}
    emoji_to_words = {'🪨': 'камень',
                      '✂️': 'ножницы',
                      '📄': 'бумага'}
    if win_counter == win:
        coins += 10
        bot.send_message(message.chat.id, f'Ты победил! Со счетом: {win_counter}:{lose_counter}\n+10 монет')
        bot.send_message(message.chat.id,
                         'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова. Для смены сложности /difficulty')
        return
    elif lose_counter == win:
        bot.send_message(message.chat.id, f'Ты проиграл! Со счетом: {lose_counter}:{win_counter}')
        bot.send_message(message.chat.id,
                         'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова. Для смены сложности /difficulty')
        return

    if user_answer not in ['🪨', '✂️', '📄'] and user_answer not in ['камень', 'ножницы', 'бумага']:
        bot.send_message(message.chat.id,
                         'Вы ввели неправильное значение. Попробуйте камень, ножницы или бумага. Или воспользуйтесь эмодзи: 🪨, ✂️, 📄')
        bot.register_next_step_handler(message, rock_paper_scissors, win_counter, lose_counter)
    else:
        if user_answer in ['🪨', '✂️', '📄']:
            user_answer = emoji_to_words[user_answer]
        result = rock_paper_scissors_check(user_answer, computer_step)
        if user_answer not in ['🪨', '✂️', '📄']:
            user_answer = words_to_emoji[user_answer]
        if result == 'Ты проиграл':
            lose_counter += 1
        elif result == 'Ты победил':
            win_counter += 1
        bot.send_message(message.chat.id, f'{result}! Вы: {user_answer}, компьютер: {words_to_emoji[computer_step]}')
        computer_step = random.choice(['камень', 'ножницы', 'бумага'])
        bot.register_next_step_handler(message, rock_paper_scissors, win_counter, lose_counter, computer_step)


def game_quiz(message, questions: dict):
    global quiz_counter, coins
    count_questions = 5
    if difficulty == 'normal':
        count_questions = 7
    elif difficulty == 'hard':
        count_questions = 10
    if quiz_counter >= count_questions:
        bot.send_message(message.chat.id, f'Кол-во правильных ответов: {win_counter}\n+{win_counter * 3} монет')
        bot.send_message(message.chat.id,
                         'Хотите сыграть еще раз?\nТогда введите команду /start и выберите эту игру снова. Для смены сложности /difficulty')
        quiz_counter = 0
        coins += 3
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(questions[list(questions.keys())[quiz_counter]][0], callback_data='true')
        item2 = types.InlineKeyboardButton(questions[list(questions.keys())[quiz_counter]][1], callback_data='false')
        item3 = types.InlineKeyboardButton(questions[list(questions.keys())[quiz_counter]][2], callback_data='false')
        items = [item1, item2, item3]
        random.shuffle(items)
        markup.add(items[0], items[1], items[2])
        bot.send_message(message.chat.id, list(questions.keys())[quiz_counter], reply_markup=markup)

    @bot.callback_query_handler()
    def callback(call):
        nonlocal count_questions
        global quiz_counter, win_counter
        if difficulty == 'normal':
            count_questions = 7
        elif difficulty == 'hard':
            count_questions = 10
        if quiz_counter >= count_questions:
            quiz_counter = 0
            win_counter = 0
        elif call.data == 'true':
            win_counter += 1
            quiz_counter += 1
            game_quiz(message, questions)
        elif call.data == 'false':
            quiz_counter += 1
            game_quiz(message, questions)
        elif call.data == 'false':
            quiz_counter += 1
            game_quiz(message, questions)


@bot.message_handler(commands=['coins'])
def coins_handler(message):
    bot.send_message(message.chat.id, f'У вас {coins} монет')
    bot.send_message(message.chat.id, f'Вы можете их зарабатывать играя в игры')


@bot.message_handler(commands=['difficulty'])
def difficulty_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton('Easy', callback_data='easy')
    item2 = types.InlineKeyboardButton('Normal', callback_data='normal')
    item3 = types.InlineKeyboardButton('Hard', callback_data='hard')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, f'Текущая сложность: {difficulty}')
    bot.send_message(message.chat.id, f'Хотите ее изменить?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'easy' or call.data == 'normal' or call.data == 'hard')
def callback_difficulty(call):
    global difficulty
    if call.data == 'easy':
        difficulty = 'easy'
    elif call.data == 'normal':
        difficulty = 'normal'
    else:
        difficulty = 'hard'
    bot.send_message(call.message.chat.id, f'Текущая сложность: {difficulty}')
    bot.send_message(call.message.chat.id, 'Сложность изменена!')


@bot.message_handler()
def text_handler(message):
    bot.send_message(message.chat.id, 'Вы ввели неправильное значение. Попробуйте /start или /coins или /difficulty')


bot.polling(none_stop=True)
