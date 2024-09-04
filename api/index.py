from atproto import Client, models
from atproto_client.utils import TextBuilder
import dotenv, os, rich
import time, requests
from flask import Flask

dotenv.load_dotenv()
user = os.getenv("BSKY_USER") ; passwd = os.getenv("BSKY_PASS")

client = Client("https://bsky.social")
rich.print(f"Loggin in as [blue]{user} [/blue] with password [red]{passwd} [/red]")
client.login(user, passwd)

defaultText = TextBuilder()
defaultText.text("✨ Olá! Para adicionar o seu projeto ao repositório, siga as seguintes instruções: \n")
defaultText.text("1. Acesse o ")
defaultText.link("repositório", "https://github.com/lunaperegrina/awesome-bsky")
defaultText.text(". \n")
defaultText.text('2. Clique no botão "fork" \n')
defaultText.text('3. Edite o arquivo "README.md", adicionando seu projeto. \n')
defaultText.text('4. Crie uma pull request para adicioná-lo ao repositório. \n')



def GetMentions() -> list[models.AppBskyNotificationListNotifications.Notification]:
  mentions = []
  Unreadnotifications = client.app.bsky.notification.get_unread_count()
  if Unreadnotifications.count > 0:
    allNotifications = client.app.bsky.notification.list_notifications(params={'limit':Unreadnotifications.count})
    for notification in allNotifications.notifications:
      if notification.reason == 'mention' and notification.is_read == False:
        mentions.append(notification)

    client.app.bsky.notification.update_seen(data={'seen_at':client.get_current_time_iso()})
    return mentions
  return []


def reply(mention: models.AppBskyNotificationListNotifications.Notification):
  parent = models.create_strong_ref(mention)
  root = models.create_strong_ref(mention.record.reply.root)

  client.post(
    text=defaultText,
    reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=root)
  )


def MainFunction():
    mentions = GetMentions()
    for mention in mentions:
      rich.print(f'[blue bold]NEW MENTION[/blue bold]: {mention.author.display_name}')
      reply(mention)
      print('Posted instructions.')
      print('\n \n \n \n')


app = Flask(__name__)

@app.route('/check')
def check():
  MainFunction()
  return 'ok'

if __name__ == '__main__':
  app.run()