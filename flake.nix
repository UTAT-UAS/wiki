{
  description = "Development shell for the UAS Software Wiki";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (python-pkgs: [
              python-pkgs.mkdocs-material
            ]))
          ];

          shellHook = ''
            echo "Start the MkDocs server with: mkdocs serve"
          '';
        };
      });
    };
}
