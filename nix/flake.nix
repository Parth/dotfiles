{
  description = "Example nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    nix-homebrew.url = "github:zhaofengli-wip/nix-homebrew";
  };

  outputs =
    inputs@{ self
    , nix-darwin
    , nixpkgs
    , home-manager
    , nix-homebrew
    ,
    }:
    let
      configuration =
        { pkgs, ... }:
        {
          nixpkgs.config.allowUnfree = true;
          nix.settings.experimental-features = "nix-command flakes";
          homebrew.enable = true;

          # Set Git commit hash for darwin-version.
          system.configurationRevision = self.rev or self.dirtyRev or null;

          environment.systemPackages = with pkgs; [
            ffmpeg_6

            fzf

            lua-language-server
            zola
            nixpkgs-fmt
            nixd
            rust-analyzer
            rustup
            lockbook
            # listing clang here makes the macOS clang act strange
          ];

          fonts.packages = with pkgs; [
            nerd-fonts.jetbrains-mono
          ];


          # Used for backwards compatibility, please read the changelog before changing.
          # $ darwin-rebuild changelog
          system.stateVersion = 6;

          system.defaults.dock.autohide = true;

          # The platform the configuration will be used on.
          nixpkgs.hostPlatform = "aarch64-darwin";


          imports = [
            ./common/fish.nix
          ];

          users.knownUsers = [ "parth" ];
          users.users.parth.uid = 501;
          system.primaryUser = "parth";

          users.users.parth = {
            home = "/Users/parth";
            shell = pkgs.fish;
          };

          system.keyboard = {
            enableKeyMapping = true;
            remapCapsLockToEscape = true;
          };
        };
    in
    {
      # Build darwin flake using:
      # $ darwin-rebuild build --flake .#simple
      darwinConfigurations.default = nix-darwin.lib.darwinSystem {
        modules = [
          configuration

          nix-homebrew.darwinModules.nix-homebrew
          {
            nix-homebrew = {
              enable = true;
              user = "parth";
            };

            homebrew = {
              enable = true;

              masApps = {
                "XCode" = 497799835;
                "Lockbook" = 1526775001;
                "Lightroom" = 1451544217;
              };

              casks = [
                "zed"
                "gimp"
                "wezterm"
                "google-chrome"
                "nikitabobko/tap/aerospace"
                "insta360-studio"
                "adobe-creative-cloud"
                "discord"
                "1password"
                "spotify"
                "chatgpt"
                "makemkv"
                "musescore"
              ];
            };
          }


          home-manager.darwinModules.home-manager
          {
            home-manager.useGlobalPkgs = true;
            home-manager.backupFileExtension = "backup";
            home-manager.useUserPackages = true;
            home-manager.users.parth = { ... }: {
              home.stateVersion = "24.05";

              imports = [
                ./common/nvim.nix
                ./common/git.nix
                ./common/xdg.nix
              ];
            };
          }
        ];

      };
    };
}
# https://github.com/dustinlyons/nixos-config/blob/8a14e1f0da074b3f9060e8c822164d922bfeec29/modules/darwin/home-manager.nix#L74
