{
  description = "Example nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ self
    , nix-darwin
    , nixpkgs
    , home-manager
    ,
    }:
    let
      configuration =
        { pkgs, ... }:
        {
          # List packages installed in system profile. To search by name, run:
          # $ nix-env -qaP | grep wget
          environment.systemPackages = with pkgs; [
            fzf
            xclip

            ripgrep
            clang

            samba

            # move these to neovim specific area 
            rust-analyzer
            rustup

            nixd

            nixpkgs-fmt
          ];

          # Necessary for using flakes on this system.
          nix.settings.experimental-features = "nix-command flakes";


          # Set Git commit hash for darwin-version.
          system.configurationRevision = self.rev or self.dirtyRev or null;

          # Used for backwards compatibility, please read the changelog before changing.
          # $ darwin-rebuild changelog
          system.stateVersion = 6;

          # The platform the configuration will be used on.
          nixpkgs.hostPlatform = "aarch64-darwin";

          programs.fish = {
            enable = true;
            shellInit = ''
              		fish_vi_key_bindings
              	'';
          };

          users.knownUsers = [ "parth" ];
          users.users.parth.uid = 501;

          users.users.parth = {
            home = "/Users/parth";
            shell = pkgs.fish;
          };
        };
    in
    {
      # Build darwin flake using:
      # $ darwin-rebuild build --flake .#simple
      darwinConfigurations."parth-macbook" = nix-darwin.lib.darwinSystem {
        modules = [
          configuration

          home-manager.darwinModules.home-manager
          {
            home-manager.useGlobalPkgs = true;
            home-manager.useUserPackages = true;
            home-manager.users.parth = { pkgs, ... }: {
              home.stateVersion = "24.05";

              programs.git = {
                enable = true;
                userName = "parth";
                userEmail = "parth@mehrotra.me";
              };

              programs.neovim = {
                enable = true;
                plugins = with pkgs.vimPlugins; [
                  nvim-web-devicons
                  telescope-nvim
                  nvim-cmp
                  cmp-nvim-lsp
                  vim-illuminate
                  lualine-nvim
                  lsp-status-nvim
                  nvim-tree-lua
                  nvim-lspconfig
                  luasnip
                  # todo replace "FabijanZulj/blame.nvim",
                ];

                extraPackages = with pkgs; [
                  lua-language-server
                  # i would like to configure this here but rustup does some wack shit
                  # rust-analyzer
                ];

                # extraLuaConfig = ''
                # 	dofile("/home/parth/dotfiles/nvim/init.lua")
                # '';
              };



              xdg.configFile = {
                "nvim" = {
                  source = /Users/parth/dotfiles/nvim;
                  recursive = true;
                };
              };

            };
          }
        ];
      };
    };
}
