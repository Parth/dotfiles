{ config, lib, pkgs, ... }:
{

  services.xserver.videoDrivers = [ "nvidia" ];

  # Load nvidia driver for Xorg and Wayland
  hardware.opengl = {
    enable = true;
    driSupport = true;
    driSupport32Bit = true;
  };

  hardware.nvidia = {

    forceFullCompositionPipeline = true;
    # Modesetting is required.
    modesetting.enable = true;

    # Nvidia power management. Experimental, and can cause sleep/suspend to fail.
    # Enable this if you have graphical corruption issues or application crashes after waking
    # up from sleep. This fixes it by saving the entire VRAM memory to /tmp/ instead 
    # of just the bare essentials.
    powerManagement.enable = false;

    # Fine-grained power management. Turns off GPU when not in use.
    # Experimental and only works on modern Nvidia GPUs (Turing or newer).
    powerManagement.finegrained = false;

    # Use the NVidia open source kernel module (not to be confused with the
    # independent third-party "nouveau" open source driver).
    # Support is limited to the Turing and later architectures. Full list of 
    # supported GPUs is at: 
    # https://github.com/NVIDIA/open-gpu-kernel-modules#compatible-gpus 
    # Only available from driver 515.43.04+
    # Currently alpha-quality/buggy, so false is currently the recommended setting.
    open = false;

    # Enable the Nvidia settings menu,
    # accessible via `nvidia-settings`.
    nvidiaSettings = true;

    # Optionally, you may need to select the appropriate driver version for your specific GPU.
    package = config.boot.kernelPackages.nvidiaPackages.stable;
  };

  # this config seemed to initially make wayland the default until I forced it to be x11 at the gdm level
  # the behavior was really strange lots of weird frame stuttering going on until x11 was the default, than
  # many problems went away.
  # I don't have screen tearing at this point, and that's generally my litmus test, but I do seem to have
  # vsync issues (which I've probably never tested for before). But I do have 2 monitors with different 
  # refresh rates, so maybe that's just my problem.
  # maybe some combination of a new driver from nvidia and wayland will solve this at some pognt

  imports = [
    "/home/parth/dotfiles/nix/common/configuration.nix"
  ];
}
