import aiohttp
import asyncio
from aiogram import F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import  Router, types
from g4f.client import AsyncClient
import g4f



router = Router()
test_channel = '-1002242059148'
aducation_channel = '-1002247217706'

client = AsyncClient()

class Order(StatesGroup):
   question = State()



@router.message(Order.question)
async def Question(message:Message,state: FSMContext):
    if message.text == "Выйти":
        kb = [[types.KeyboardButton(text="Подписаться на канал")], [types.KeyboardButton(text="Нейросеть ProfitStars")]]
        keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
        await message.answer("Вы вышли из бота", reply_markup=keybord)
        await state.clear()
        return None
    await message.answer ("Бот думает...")
    kb = [[types.KeyboardButton(text="Выйти")]]
    keybord = (types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard= True))
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{message.text}"}], provider = g4f.Provider.You
        )
        await message.answer(response.choices[0].message.content, reply_markup=keybord)
        await state.set_state(Order.question.state)
    except:
        await message.answer("Произошла ошибка, попробуйте позже!")


