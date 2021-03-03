# Floating Macro Panel
# ====================
#
# Copyright 2021 Florian Pircher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import objc
from AppKit import (
    NSApplicationWillBecomeActiveNotification,
    NSApplicationWillResignActiveNotification,
    NSFloatingWindowLevel,
    NSNormalWindowLevel,
    NSNotificationCenter,
    NSOperationQueue,
    NSWindowAbove,
)
from GlyphsApp import (Glyphs, LogError)
from GlyphsApp.plugins import GeneralPlugin


class FloatingMacroPanel(GeneralPlugin):
    macroPanel = None
    defaultLevel = NSNormalWindowLevel

    @objc.python_method
    def settings(self):
        self.name = "Floating Macro Panel"

    @objc.python_method
    def start(self):
        for window in Glyphs.windows():
            if window.className() == "GSMacroWindow":
                self.macroPanel = window

        if not self.macroPanel:
            LogError("Floating Macro Panel: could not find macro panel.")
            return

        self.macroPanel.setLevel_(NSFloatingWindowLevel)

        NSNotificationCenter.defaultCenter().addObserverForName_object_queue_usingBlock_(
            NSApplicationWillResignActiveNotification,
            None,
            NSOperationQueue.mainQueue(),
            lambda x: self.willResignActive(x),
        )

        NSNotificationCenter.defaultCenter().addObserverForName_object_queue_usingBlock_(
            NSApplicationWillBecomeActiveNotification,
            None,
            NSOperationQueue.mainQueue(),
            lambda x: self.willBecomeActive(x),
        )

    @objc.python_method
    def willResignActive(self, notification):
        self.macroPanel.setLevel_(NSNormalWindowLevel)
        self.macroPanel.orderWindow_relativeTo_(NSWindowAbove, 0)

    @objc.python_method
    def willBecomeActive(self, notification):
        self.macroPanel.orderFrontRegardless()
        self.macroPanel.setLevel_(NSFloatingWindowLevel)
        # This is the only way I know (time.sleep etc do not work) how to delay subsequent processing to prevent the main window to first show up on top to be covered by the macro panel in a split of a second later.
        # The window-order-flickering still happends sometimes, but it is shorter and less frequent.
        print("\u200B" * 240, end="")
