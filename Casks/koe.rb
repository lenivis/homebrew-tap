cask "koe" do
  version "1.0.0"
  sha256 "9e0cfa35723e157aecb386133750595d5cecddd6902971e73aace56005dabf96"

  url "https://github.com/YIPG/koe-releases/releases/download/v#{version}/koe-#{version}-macos-arm64.zip"
  name "koe"
  desc "Menu bar dictation for Japanese and English"
  homepage "https://saykoe.com/"

  livecheck do
    url "https://github.com/YIPG/koe-releases/releases/latest/download/appcast.xml"
    strategy :sparkle
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :ventura

  app "koe.app"

  uninstall quit: "com.koe.dictation"

  zap trash: [
    "~/Library/Application Support/com.koe.dictation",
    "~/Library/Caches/com.koe.dictation",
    "~/Library/HTTPStorages/com.koe.dictation",
    "~/Library/Preferences/com.koe.dictation.plist",
    "~/Library/Saved Application State/com.koe.dictation.savedState",
  ]
end
