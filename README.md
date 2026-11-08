# PatcherPublic_template
Template duquel partir pour faire un patcheur auto public pour une sortie de patch

Créez un environnement virtuel

    python -m venv .venv

(powershell)

    .venv\Scripts\Activate.ps1
 
(linux)

    source .venv/bin/activate

Installer les dépendances

    pip install -r requirements.txt

S’il vous faut des dépendances en plus, pip install la dépendance dans le venv puis :

    pip freeze > requirements.txt

Mettez le logo du jeu dans resources au nom `game-logo.png` et lancez la ligne suivante pour compiler les ressources.

    pyside6-rcc resources/resources.qrc -o patcher/ui/resources_rc.py

Pour run

    python -m patcher.main

Pour build

    pyinstaller patcheur_auto.spec

Les dossiers `patch` et `tool` seront automatiquement copié dans dist.

#

Il faut renseigner le fichiers config.py, tool.py

## config.py

C’est ici que les paramètres spécifiques au projet. Il faut y renseigner les id du drive, les chemins de dossiers, etc.

## tool.py

C’est ici que sont faite les commande des outils cmd pour repack le jeu.
