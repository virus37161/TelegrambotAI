import asyncio
import aiohttp
import logging
import sys
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.types import ChatMemberUpdated
from tokens import TOKEN
import views
from aiogram.fsm.context import FSMContext
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from g4f.client import AsyncClient
import g4f
from Teksts import invite_tekst
from filters.chat_type import ChatTypeFilter
dp = Dispatcher()

class Order(StatesGroup):
    question = State()
    check_ai = State()

test_channel = '-1001215291753'
aducation_channel = '-1002213034840'
chat_channel = '-1001815152668'

client = AsyncClient()
dp.message.filter(ChatTypeFilter(chat_type ="private"))

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    kb = [[types.KeyboardButton(text="Подписаться на канал")], [types.KeyboardButton(text = "Нейросеть ProfitStars")]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
    await message.answer (text = invite_tekst, reply_markup=keybord, parse_mode="Markdown")

async def on_user_join(event: ChatMemberUpdated): # отправка сообщения новому пользователю
    if str(event.chat.id) == chat_channel:
        msg = await event.answer(views.join_message(event.new_chat_member.user.first_name))
        await message_del(msg.message_id, msg.chat.id)

async def message_del(id,chat): # удаление сообщения
    await asyncio.sleep(10)
    await bot.delete_message(chat,id)

async def on_user_left(event: ChatMemberUpdated):#удаление пользователя из приватного канала, если он покинул основной
    if str(event.chat.id) == test_channel:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"https://api.telegram.org/bot{TOKEN}/KickChatMember?chat_id={aducation_channel}&user_id={event.from_user.id}") as resp:
                None


dp.chat_member.register(on_user_join, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
dp.chat_member.register(on_user_left, ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))

@dp.message(F.text == "Нейросеть ProfitStars")
async def join_ai(message:Message, state:FSMContext):
    await ai(message, state)

@dp.message(Order.check_ai)
async def ai(message:Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Проверить подписку ✅")], [types.KeyboardButton (text = 'Выйти')]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
    if message.text == "Выйти":
        kb1 = [[types.KeyboardButton(text="Подписаться на канал")], [types.KeyboardButton(text="Нейросеть ProfitStars")]]
        keybord1 = (types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True, one_time_keyboard=True))
        await message.answer("Вы вышли из бота", reply_markup=keybord1)
        await state.clear()
        return None
    checked = await check(message)
    if checked == True:
        await state.clear()
        await Question_command(message,state)
    else:
        await message.answer(f"❌ Вы не подписаны на канал:\nhttps://t.me/ProfitStars_blog", reply_markup=keybord)
        await state.set_state(Order.check_ai.state)


@dp.message(F.text=="Подписаться на канал")# Проверка
async def start(message: Message):
    kb = [[types.KeyboardButton(text="Подписаться на канал")], [types.KeyboardButton(text="Нейросеть ProfitStars")]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))
    checked = await check(message)
    if checked == True:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"https://api.telegram.org/bot{TOKEN}/createChatInviteLink?chat_id={aducation_channel}&member_limit=1") as resp:
                r = await resp.json()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            url=f"https://api.telegram.org/bot{TOKEN}/unbanChatMember?chat_id={aducation_channel}&user_id={message.from_user.id}&only_if_banned") as respp:
                        None
                await message.answer(f"Вы подписаны на основной канал\n⭐\n\nВот ссылка для доступа:\n{r['result']['invite_link']}\n\n\
Добро пожаловать и удачи в мире\nкриптовалют!", reply_markup=keybord)
    else:
            await message.answer(f"❌ Вы не подписаны на канал:\nhttps://t.me/ProfitStars_blog",reply_markup=keybord)

async def check(message:Message):
    user_channel_status = await bot.get_chat_member(chat_id=test_channel, user_id=message.from_user.id)
    if str(user_channel_status.status) == 'ChatMemberStatus.MEMBER' or str(user_channel_status.status) == 'ChatMemberStatus.ADMINISTRATOR' or str(user_channel_status.status) == 'ChatMemberStatus.CREATOR':
        checked = True
    else:

        checked = False
    return checked

async def Question_command(message:Message,state: FSMContext):
    kb = [[types.KeyboardButton(text="Выйти")]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
    await message.answer("Задайте свой вопрос", reply_markup = keybord)
    await state.set_state(Order.question.state)

@dp.message(Order.question)
async def Question(message:Message,state: FSMContext):
    if message.text == "Выйти":
        kb = [[types.KeyboardButton(text="Подписаться на канал")], [types.KeyboardButton(text="Нейросеть ProfitStars")]]
        keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
        await message.answer("Вы вышли из нейросети", reply_markup=keybord)
        await state.clear()
        return None
    bot_think = await message.answer ("Нейросеть думает...")
    kb = [[types.KeyboardButton(text="Выйти")]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard= True))
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{message.text}"}], provider = g4f.Provider.You
        )
        await message.answer(response.choices[0].message.content, reply_markup=keybord)
        await bot.delete_message(bot_think.chat.id, bot_think.message_id)
        await state.set_state(Order.question.state)
    except:
        await message.answer("Произошла ошибка, попробуйте позже!")


bot = Bot(TOKEN)
async def main() -> None:
   await dp.start_polling(bot)

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())