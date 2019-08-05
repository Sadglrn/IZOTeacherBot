from config import TOKEN, TYPE_PROXY, IP
import bot

if __name__ == '__main__':
	a = bot.Bot(TOKEN, TYPE_PROXY, IP)
	a.run()
