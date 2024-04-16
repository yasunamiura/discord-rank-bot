import discord
from discord.ext import commands
from discord import app_commands
import os

GUILD_ID = int(os.getenv('MY_GUILD_ID'))  # 環境変数からサーバーIDを取得


# カスタムしたBotクラスを作成
class MyBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.default()  # デフォルトのインテントを使用
    super().__init__(command_prefix='/', intents=intents)

  async def setup_hook(self):
    # 特定のギルドにコマンドを登録
    guild = discord.Object(id=GUILD_ID)
    self.tree.add_command(rank_command, guild=guild)  # 更新したrank_commandを追加
    await self.tree.sync(guild=guild)


bot = MyBot()


# ランクと次のランクアップまでに必要な投稿数を計算する関数
def calculate_rank_and_next(counter):
  if counter <= 5:
    next_posts_needed = 6 - counter  # レベル1からランクアップするための投稿数
  else:
    # レベル2以降の計算
    current_level = (counter - 1) // 5
    next_level_posts = (current_level + 1) * 5
    next_posts_needed = next_level_posts + 1 - counter

    # スターとダイヤの表現のための計算
    stars = '⭐️' * ((current_level + 1) % 5)
    diamonds = '💎' * ((current_level + 1) // 5)
    rank_display = f"Level {current_level + 1} {stars}{diamonds}"

    if current_level >= 99:  # レベル100以上の扱い
      rank_display = "Level 100 💎"
      next_posts_needed = None  # レベル100以上ではランクアップなし

    return rank_display, next_posts_needed

  return "Level 1 ⭐️", next_posts_needed


@bot.tree.command(name="rank",
                  description="自分の#アウトプットチャンネルでの現在のランクと次のランクアップまでの必要投稿数を表示します")
async def rank_command(interaction: discord.Interaction):
  output_channel = discord.utils.get(interaction.guild.text_channels,
                                     name="アウトプット")
  if not output_channel:
    await interaction.response.send_message("#アウトプットチャンネルが見つかりません。",
                                            ephemeral=True)
    return

  counter = 0
  async for message in output_channel.history(limit=None):
    if message.author == interaction.user:
      counter += 1

  rank, posts_to_next = calculate_rank_and_next(
      counter)  #   ランクと次のランクアップまで必要な投稿数を取得

  # 次のランクアップまでの投稿数を含む応答メッセージを構築
  if posts_to_next is not None:
    message_to_next_rank = f"次のランクアップまで **{posts_to_next}件**の投稿が必要です！✨"
  else:
    message_to_next_rank = "最高ランクに達しました！おめでとうございます！🎉"

  response_message = (
      f"✨**🏆スキカレランク🏆✨**\n{interaction.user.display_name}さん!\n\n"
      f"#アウトプット報告で **{counter}件**の投稿をしました！🎉😊\n\n"
      f"**現在のランク: {rank}**\n\n"
      f"{message_to_next_rank}")

  await interaction.response.send_message(response_message, ephemeral=True)


# Botを起動
bot.run(os.getenv('TOKEN'))
