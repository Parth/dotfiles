{ ... }:
{
  programs.git = {
    enable = true;
    userName = "parth";
    userEmail = "parth@mehrotra.me";
    extraConfig = {
      push.default = "current";
      pull.default = "current";
      branch.autoSetupMerge = "true";
    };
  };
}
