from config import TOKEN, TYPE_PROXY, IP
import bot

if __name__ == '__main__':
    app = bot.Bot(TOKEN, TYPE_PROXY, IP)
    app.run()
