/*
 *
 * Licensed under the Apache License, Version 2.0 (the “License”);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an “AS IS” BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { createChatBotMessage } from "react-chatbot-kit";

const botName: string = "CrapBot";

interface Config {
  initialMessages: any[];
  botName: string;
  state: Record<string, unknown>;
  customStyles: {
    botMessageBox: {
      backgroundColor: string;
    };
    chatButton: {
      backgroundColor: string;
    };
  };
}

const config: Config = {
  initialMessages: [
    createChatBotMessage(
      `Hi, Welcome to crAPI! I'm ${botName}, and I'm here to be exploited.`,
      {},
    ),
  ],
  botName,
  state: {},
  customStyles: {
    botMessageBox: {
      backgroundColor: "#376B7E",
    },
    chatButton: {
      backgroundColor: "#5ccc9d",
    },
  },
};

export default config;
