import random
import os
import StringIO
import tweepy

from chromachipper import get_colours_from_message, make_chromachip_png

twitter_id = int(os.environ.get('TWITTER_ID'))
consumer_token = os.environ.get('CONSUMER_TOKEN')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_secret = os.environ.get('ACCESS_SECRET')


class ChromachipStreamListener(tweepy.StreamListener):

    REPLIES = [
        "You're welcome!",
        "Enjoy!",
        "Here you are!",
        "Here's your Chroma Chip!",
        "Nice one!",
        "Colo(u)rs!",
        "Huetiful!",
        "There you go!",
        "What's better than chips? Chroma Chips!",
        "Looking good!",
        "No probs!",
        "I made this especially for you!",
        "Great!",
    ]

    def __init__(self, *args, **kwargs):
        super(ChromachipStreamListener, self).__init__(*args, **kwargs)
        self.last_reply = None

    def on_status(self, status):
        if status.in_reply_to_user_id == twitter_id:
            colours = get_colours_from_message(status.text)
            if colours:
                print("Sending a ChromaChip to @%s" % status.user.screen_name)
                self.reply_to_status(status.user.screen_name, status.id, colours)
            # else:
            #     print("No colours to reply to.")
        return True

    def on_error(self, status_code):
        print("Got an error with code %s" % str(status_code))
        return True

    def on_timeout(self):
        print("Timed out...")
        return True

    def get_random_reply(self):
        """
        Randomly choose a non-repeating reply from the REPLIES list.
        """
        reply = random.choice(self.REPLIES)
        if reply is not self.last_reply:
            self.last_reply = reply
            return reply
        else:
            return self.get_random_reply()

    def reply_to_status(self, screen_name, id, colours):
        """
        Send a reply to screen_name with an attached chromachip.
        """
        try:
            string_buffer = StringIO.StringIO()
            string_buffer.write(make_chromachip_png(colours))
            string_buffer.seek(0)

            api.update_with_media('chromachip.png', '@%s %s' % (screen_name, self.get_random_reply()), in_reply_to_status_id=id, file=string_buffer)
        except tweepy.error.TweepError as e:
            print("An error! %s " % e)


if __name__ == '__main__':
    listener = ChromachipStreamListener()
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    stream = tweepy.Stream(auth, listener)
    stream.userstream("with=user")
