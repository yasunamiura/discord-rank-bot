import discord
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask

GUILD_ID = int(os.getenv('MY_GUILD_ID'))  # 環境変数からサーバーIDを取得
TOKEN = os.getenv('TOKEN')  # Botのトークン

app = Flask(__name__)


@app.route('/')
def home():
  return "Hello, World from Flask!"


def run_flask():
  app.run(host="0.0.0.0", port=8000, debug=False)


class MyBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.default()  # デフォルトのインテントを使用
    super().__init__(command_prefix='/', intents=intents)

  async def setup_hook(self):
    guild = discord.Object(id=GUILD_ID)
    self.tree.add_command(rank_command, guild=guild)
    await self.tree.sync(guild=guild)

    # Flaskサーバーを別スレッドで起動
    flask_thread = Thread(target=run_flask)
    flask_thread.start()


bot = MyBot()


def calculate_rank_and_next(counter):
  if counter <= 5:
    next_posts_needed = 6 - counter
  else:
    current_level = (counter - 1) // 5
    next_level_posts = (current_level + 1) * 5
    next_posts_needed = next_level_posts + 1 - counter

    stars = '⭐️' * ((current_level + 1) % 5)
    diamonds = '💎' * ((current_level + 1) // 5)
    rank_display = f"Level {current_level + 1} {stars}{diamonds}"

    if current_level >= 99:
      rank_display = "Level 100 💎"
      next_posts_needed = None
    return rank_display, next_posts_needed

  return "Level 1 ⭐️", next_posts_needed


@bot.tree.command(name="rank",
                  description="自分の#アウトプットチャンネルでの現在のランクと次のランクアップまでの必要投稿数を表示します")
async def rank_command(interaction: discord.Interaction):
  output_channel = discord.utils.get(interaction.guild.text_channels,
                                     name="アウトプット")
  if not output_channel:
    response = "#アウトプットチャンネルが見つかりません。"
    if interaction.response.is_done():
      await interaction.followup.send(response, ephemeral=True)
    else:
      await interaction.response.send_message(response, ephemeral=True)
    return

  counter = 0
  async for message in output_channel.history(limit=None):
    if message.author == interaction.user:
      counter += 1

  rank, posts_to_next = calculate_rank_and_next(counter)

  if posts_to_next is not None:
    message_to_next_rank = f"次のランクアップまで **{posts_to_next}件**の投稿が必要です！✨"
  else:
    message_to_next_rank = "最高ランクに達しました！おめでとうございます！🎉"

  response_message = (
      f"✨**🏆スキカレランク🏆✨**\n{interaction.user.display_name}さん!\n\n"
      f"#アウトプット報告で **{counter}件**の投稿をしました！🎉😊\n\n"
      f"**現在のランク: {rank}**\n\n"
      f"{message_to_next_rank}")

  if interaction.response.is_done():
    await interaction.followup.send(response_message, ephemeral=True)
  else:
    await interaction.response.send_message(response_message, ephemeral=True)


# Botを起動
bot.run(TOKEN)
