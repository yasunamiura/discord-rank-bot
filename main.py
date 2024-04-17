import discord
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask

GUILD_ID = int(os.getenv('MY_GUILD_ID'))  # 環境変数からサーバーIDを取得
TOKEN = os.getenv('TOKEN')  # Botのトークン

app = Flask(__name__)from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.BIGINT, primary_key=True)
    username = db.Column(db.VARCHAR)
    join_date = db.Column(db.DATE)
    last_active = db.Column(db.DATE)


class Output(db.Model):
    __tablename__ = 'outputs'

    output_id = db.Column(db.BIGINT, primary_key=True)
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'))
    post_date = db.Column(db.DATE)
    content = db.Column(db.TEXT)
    validated = db.Column(db.Boolean)


class VoiceChannelActivity(db.Model):
    __tablename__ = 'voice_channel_activities'

    activity_id = db.Column(db.BIGINT, primary_key=True)
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'))
    enter_time = db.Column(db.TIMESTAMP)
    exit_time = db.Column(db.TIMESTAMP)
    duration = db.Column(db.INTEGER)


class DailyOutputCount(db.Model):
    __tablename__ = 'daily_output_counts'

    count_id = db.Column(db.BIGINT, primary_key=True)
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'))
    post_date = db.Column(db.DATE)
    count = db.Column(db.INT)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
db = SQLAlchemy(app)

# Import your models here

# Create the database tables
db.create_all()

# Run the Flask app
if __name__ == '__main__':
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
