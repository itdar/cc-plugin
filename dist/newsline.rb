# Homebrew formula for newsline (cc-plugin).
# Copy this into your tap:  itdar/homebrew-tap  ->  Formula/newsline.rb
# Then users install with:   brew install itdar/tap/newsline
#
# Release steps (see cc-plugin README):
#   1) git tag v0.1.0 && git push --tags   (on itdar/cc-plugin)
#   2) shasum -a 256 the tarball URL below, paste into `sha256`
class Newsline < Formula
  desc "Locale-aware one-line news in your Claude Code status line"
  homepage "https://github.com/itdar/cc-plugin"
  url "https://github.com/itdar/cc-plugin/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_TARBALL_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    libexec.install "newsline", "statusline.sh", "refresh.sh",
                    "fetch.py", "resolve.py", "feeds.json"
    bin.install_symlink libexec/"newsline"
  end

  def caveats
    <<~EOS
      Wire it into Claude Code (composes with your existing status line):
        newsline init
    EOS
  end

  test do
    assert_match "newsline", shell_output("#{bin}/newsline help")
  end
end
