import time
import re
import requests
from slackclient import SlackClient
from bs4 import BeautifulSoup
import json

# constants
SLACK_BOT_TOKEN = 'YOUR_SLACK_BOT_TOKEN'
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+)>(.*)"
PHG_CARD_URL = "https://play.plaidhatgames.com/views/ajax"
PHG_FORM_DATA_BASE = data = [
  ('title_op', 'contains'),
  ('title', ''),
  ('field_type_value', 'All'),
  ('combine', ''),
  ('combine_2', 'All'),
  ('combine_1', 'All'),
  ('field_unit_attack_value_value_op', '='),
  ('field_unit_attack_value_value[value]', ''),
  ('field_unit_attack_value_value[min]', ''),
  ('field_unit_attack_value_value[max]', ''),
  ('field_unit_life_value_value_op', '='),
  ('field_unit_life_value_value[value]', ''),
  ('field_unit_life_value_value[min]', ''),
  ('field_unit_life_value_value[max]', ''),
  ('field_unit_recovery_value_value_op', '='),
  ('field_unit_recovery_value_value[value]', ''),
  ('field_unit_recovery_value_value[min]', ''),
  ('field_unit_recovery_value_value[max]', ''),
  ('field_associated_product_title', 'All'),
  ('view_name', 'ashes_card_browser'),
  ('view_display_id', 'page_1'),
  ('view_args', ''),
  ('view_path', 'ashes/cards'),
  ('view_base_path', 'ashes/cards'),
  ('view_dom_id', '1f01b391e1d5150ef0df05072a610701'),
  ('pager_element', '0'),
  ('ajax_html_ids[]', 'main-content'),
  ('ajax_html_ids[]', 'views-exposed-form-ashes-card-browser-page-1'),
  ('ajax_html_ids[]', 'edit-title-wrapper'),
  ('ajax_html_ids[]', 'edit-title-op'),
  ('ajax_html_ids[]', 'edit-title'),
  ('ajax_html_ids[]', 'edit-field-type-value-wrapper'),
  ('ajax_html_ids[]', 'edit-field-type-value'),
  ('ajax_html_ids[]', 'edit-combine-wrapper'),
  ('ajax_html_ids[]', 'edit-combine'),
  ('ajax_html_ids[]', 'edit-combine-2-wrapper'),
  ('ajax_html_ids[]', 'edit-combine-2'),
  ('ajax_html_ids[]', 'edit-combine-1-wrapper'),
  ('ajax_html_ids[]', 'edit-combine-1'),
  ('ajax_html_ids[]', 'edit-field-unit-attack-value-value-wrapper'),
  ('ajax_html_ids[]', 'edit-field-unit-attack-value-value-op'),
  ('ajax_html_ids[]', 'edit-field-unit-attack-value-value-value'),
  ('ajax_html_ids[]', 'edit-field-unit-attack-value-value-min'),
  ('ajax_html_ids[]', 'edit-field-unit-attack-value-value-max'),
  ('ajax_html_ids[]', 'edit-field-unit-life-value-value-wrapper'),
  ('ajax_html_ids[]', 'edit-field-unit-life-value-value-op'),
  ('ajax_html_ids[]', 'edit-field-unit-life-value-value-value'),
  ('ajax_html_ids[]', 'edit-field-unit-life-value-value-min'),
  ('ajax_html_ids[]', 'edit-field-unit-life-value-value-max'),
  ('ajax_html_ids[]', 'edit-field-unit-recovery-value-value-wrapper'),
  ('ajax_html_ids[]', 'edit-field-unit-recovery-value-value-op'),
  ('ajax_html_ids[]', 'edit-field-unit-recovery-value-value-value'),
  ('ajax_html_ids[]', 'edit-field-unit-recovery-value-value-min'),
  ('ajax_html_ids[]', 'edit-field-unit-recovery-value-value-max'),
  ('ajax_html_ids[]', 'edit-field-associated-product-title-wrapper'),
  ('ajax_html_ids[]', 'edit-field-associated-product-title'),
  ('ajax_html_ids[]', 'edit-submit-ashes-card-browser'),
  ('ajax_html_ids[]', 'reset-ashes-card-browser'),
  ('ajax_html_ids[]', 'block-phg-ashes-ashes-deckbuild-block'),
  ('ajax_page_state[theme]', 'skifi'),
  ('ajax_page_state[theme_token]', 'dZHJynxsIr7-xlm5Ffrks9MR9Eq59qDOFBWhG4T-VfE'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/system/system.base.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/system/system.menus.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/system/system.messages.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/system/system.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/date/date_api/date.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/date/date_popup/themes/datepicker.1.7.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/comment/comment.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/esign/css/esign.css]', '1'),
  ('ajax_page_state[css][modules/node/node.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/field/field.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/search/search.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/views/css/views.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/user/user.base.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/ckeditor/css/ckeditor.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/forum/forum.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/omega/omega/css/modules/user/user.theme.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/ctools/css/ctools.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/pdm/pdm.css]', '1'),
  ('ajax_page_state[css][sites/all/modules/rate/rate.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/phgplayashes/css/phgplayashes.normalize.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/phgplayashes/css/phgplayashes.hacks.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/phgplayashes/css/phgplayashes.styles.css]', '1'),
  ('ajax_page_state[css][sites/all/themes/phgplayashes/css/phgplayashes.no-query.css]', '1'),
  ('ajax_page_state[js][0]', '1'),
  ('ajax_page_state[js][sites/all/modules/jquery_update/replace/jquery/1.7/jquery.min.js]', '1'),
  ('ajax_page_state[js][misc/jquery.once.js]', '1'),
  ('ajax_page_state[js][misc/drupal.js]', '1'),
  ('ajax_page_state[js][sites/all/themes/omega/omega/js/no-js.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/jquery_update/replace/ui/external/jquery.cookie.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/jquery_update/replace/misc/jquery.form.min.js]', '1'),
  ('ajax_page_state[js][misc/ajax.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/jquery_update/js/jquery_update.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/pdm/pdm.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/better_exposed_filters/better_exposed_filters.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/views_load_more/views_load_more.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/ctools/js/dependent.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/views/js/base.js]', '1'),
  ('ajax_page_state[js][misc/progress.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/views/js/ajax_view.js]', '1'),
  ('ajax_page_state[js][sites/all/modules/google_analytics/googleanalytics.js]', '1'),
  ('ajax_page_state[js][sites/all/themes/phgplayashes/js/phgplayashes.behaviors.js]', '1'),
  ('ajax_page_state[js][sites/all/themes/phgplayashes/js/ashescards.js]', '1'),
  ('ajax_page_state[jquery_version]', '1.7'),
]


class CardBot:
    slack_client = None
    cardbot_id = None

    def __init__(self, testing=False):
        # Instantiate Slack client
        self.slack_client = SlackClient(SLACK_BOT_TOKEN)

        if self.slack_client.rtm_connect(with_team_state=False):
            print("Card Bot connected and running!")
            self.cardbot_id = self.slack_client.api_call("auth.test")["user_id"]
            while not testing:
                command, channel = self.parse_bot_commands(self.slack_client.rtm_read())
                if command:
                    self.handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed.")

    def parse_bot_commands(self, slack_events):
        """
        Parse events from slack to find bot commands.
        If the  event matches the bot, it returns the command and the channel.
        Else, it returns None, None
        :param slack_events: A list of Slack events
        :return: Tuple, either (command, channel) or (None, None)
        """
        for event in slack_events:
            if event['type'] == 'message' and not 'subtype' in event:
                user_id, message = self.parse_direct_mention(event['text'])
                if user_id == self.cardbot_id:
                    return message, event['channel']
        return None, None

    def parse_direct_mention(self, message_text):
        """
        Determines whether it's a direct mention, and returns whether the user directly mentioned was me
        :param message_text: The whole message's text
        :return: Either the user ID and remaining message text, or None, None
        """
        matches = re.search(MENTION_REGEX, message_text)

        if matches:
            return matches.group(1), matches.group(2).strip()
        else:
            return None, None

    def handle_command(self, command, channel):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=self.getCardInfo(command)
        )

    def getCardInfo(self, command):
        form_data = PHG_FORM_DATA_BASE
        form_data[1] = ("title", command)

        r = requests.post(
            url=PHG_CARD_URL,
            data=form_data
        )
        response_data = json.loads(r.text)

        xml_data = BeautifulSoup(response_data[2]['data'], "html.parser")

        images = xml_data.find_all('img')
        if len(images) > 0:
            image = images[0]
        else:
            return """I couldn't find a card for {}. Please try again.""".format(command)

        return image.parent.parent.find_all("a")[0].text + ' - ' + image['src']

if __name__ == '__main__':
    bot = CardBot()
