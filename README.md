# Talking-Head Reels

> **Skill d'agent IA** qui transforme une vidéo face caméra en **reel vertical 9:16** prêt à publier (Instagram Reels, TikTok, YouTube Shorts) : coupes de pauses, sous-titres kinétiques, B-roll, split screens, transitions, grain, voix masterisée à −14 LUFS. Tout est rendu par du code (Python + ffmpeg/libass), sans After Effects ni logiciel de montage.

[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
[![Plateformes](https://img.shields.io/badge/plateformes-macOS%20%7C%20Windows-lightgrey.svg)](#prérequis)
[![MCP](https://img.shields.io/badge/MCP-Pixabay%20%2B%20thesvg-orange.svg)](#5-installer-les-mcp-utilisés-par-le-skill)
[![Agent Skills](https://img.shields.io/badge/format-SKILL.md-purple.svg)](https://opencode.ai/v2/docs/skills)

---

## Sommaire

1. [Ce que fait le skill](#1-ce-que-fait-le-skill)
2. [Comment ça marche](#2-comment-ça-marche)
3. [Prérequis](#3-prérequis)
4. [Installer le skill](#4-installer-le-skill)
5. [Installer les MCP utilisés par le skill](#5-installer-les-mcp-utilisés-par-le-skill)
6. [Utilisation complète](#6-utilisation-complète)
Démo. [Démo (avant/après)](#demo-avantaprès)
7. [Structure du dépôt](#7-structure-du-dépôt)
8. [Sources gratuites, licences et attribution](#8-sources-gratuites-licences-et-attribution)
9. [Dépannage](#9-dépannage)
10. [FAQ](#10-faq)
11. [Licence](#11-licence)

---

## 1. Ce que fait le skill

À partir d'**une seule vidéo d'une personne qui parle face caméra**, l'agent :

- transcrit la voix et **coupe les pauses, hésitations et respirations** ;
- masterise l'audio à environ **−14 LUFS** ;
- écrit un **beat sheet** (plan de montage) validé avec vous ;
- source le **B-roll gratuitement** (votre matériel, Pixabay, Wikimedia Commons, icônes thesvg) ;
- écrit un **EDL** (edit decision list) : tout le montage est un fichier JSON reproductible ;
- rend des **stills de contrôle**, puis la vidéo finale ;
- gère les **rounds de révision** versionnés (`v1`, `v2`, …) sans jamais écraser un rendu validé.

**Sortie :** `1080×1920`, H.264 (CRF 12, yuv420p, BT.709), AAC 320 kbps 48 kHz, `+faststart`, voix à ~−14 LUFS.

**Look par défaut :** éditorial et rapide — Anton + Didot (substitués par Playfair Display sur Windows), palette rouge / blanc / noir et blanc, gros mots kinétiques, inserts B-roll, splits avec le présentateur, grain et vignette.

> Le skill est **gratuit par défaut** : aucune génération d'image payante, aucun crédit. Un appendice optionnel (Higgsfield / Seedance) existe pour la génération IA, mais il n'est utilisé que si vous le demandez explicitement.

---

## 2. Comment ça marche

| Étape | Ce qui se passe | Script |
|---|---|---|
| 0 | Diagnostic de la machine | `scripts/check_setup.py` |
| 1 | Préparation, transcription, coupe des pauses, mastering | `prepare_project.py`, `transcribe.py`, `cut_pauses.py`, `master_audio.py` |
| 2 | Plan éditorial (beat sheet) | décision de l'agent |
| 3 | Sourcing B-roll / logos | MCP Pixabay, MCP thesvg, API Wikimedia |
| 4 | Écriture et validation de l'EDL | `validate_edl.py` |
| 5 | Stills de QA puis rendu | `render_reel.py` |
| 6 | Révisions versionnées | `edl_vN.json`, `_vN.mp4` |

---

## 3. Prérequis

### Matériel / OS

- **macOS 13+** (cible native) ou **Windows 10/11**.
- Le moteur de rendu est **neutre côté plateforme** : aucun blocage macOS dans les scripts de rendu.
- Les **mattes Apple Vision** (silhouettes découpées) nécessitent macOS + `swiftc` ; elles sont **optionnelles** et simplement ignorées sur Windows.

### Logiciels

| Outil | Version | Notes |
|---|---|---|
| Python | 3.9+ | avec `numpy`, `faster-whisper`, `imageio-ffmpeg` |
| ffmpeg | build récent **avec libass** | macOS : `brew install ffmpeg` · Windows : build « full » de [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) |
| ffprobe | même build que ffmpeg | souvent oublié sur Windows |
| Git | any | pour cloner le skill |
| Node.js | 18+ | requis uniquement pour les serveurs MCP (`npx`) |
| Xcode CLT | optionnel | uniquement pour les mattes Vision (`swiftc`) |

Vérifications rapides :

```bash
python3 --version
ffmpeg -version
ffmpeg -filters | grep ass          # macOS / Linux
ffmpeg -filters | findstr ass       # Windows PowerShell
node --version
```

> Sur Windows, `python3` n'existe souvent pas : utilisez `python` ou `py -3` dans toutes les commandes de ce README.

### Polices

- **macOS** : Anton est fourni (`assets/fonts/`) ; Didot et Helvetica Neue viennent du système.
- **Windows** : les substituts libres **Playfair Display** (400 / 700 / italic) et **Inter Medium** sont fournis dans `assets/fonts/win/` (licence OFL). Voir [§ 3.1](#31-windows--activer-les-polices-libres).

#### 3.1 Windows — activer les polices libres

1. Renseignez la variable d'environnement utilisateur `REEL_FONT_FILES` avec les **4 chemins séparés par des points-virgules** :

```powershell
$f = "$env:USERPROFILE\.config\opencode\skills\talking-head-reels\assets\fonts\win"
setx REEL_FONT_FILES "$f\PlayfairDisplay_700_bold.ttf;$f\PlayfairDisplay_400_normal.ttf;$f\PlayfairDisplay_400_italic.ttf;$f\Inter_500_normal.ttf"
```

2. **Rouvrez le terminal** (la variable n'est héritée que par les nouveaux processus).
3. Dans chaque EDL, ajoutez l'override de polices :

```json
"fonts": {
  "anton": "Anton-Regular",
  "serif": "PlayfairDisplay-Bold",
  "didot": "PlayfairDisplay-Regular",
  "sub": "Inter-Medium"
}
```

> Le moteur extrait lui-même ces fichiers dans le dossier de polices de libass via son hook `REEL_FONT_FILES` (`textass.py`). Aucun script du moteur n'est modifié.

---

## 4. Installer le skill

Le dépôt **est** le dossier du skill : `SKILL.md` est à la racine. Le clone se fait donc directement dans le dossier de skills de votre agent.

### 4.1 OpenCode (recommandé)

**macOS / Linux**

```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/SergeoDev01/talking-head-reels.git \
  ~/.config/opencode/skills/talking-head-reels
```

**Windows PowerShell**

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skills" | Out-Null
git clone https://github.com/SergeoDev01/talking-head-reels.git `
  "$env:USERPROFILE\.config\opencode\skills\talking-head-reels"
```

OpenCode détecte le skill à chaud (file watcher). Sinon, `/reload` dans le TUI, ou redémarrez le service :

```bash
opencode service restart
```

### 4.2 Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/SergeoDev01/talking-head-reels.git \
  ~/.claude/skills/talking-head-reels
```

### 4.3 Autres agents (Codex, Amp, etc. — format « Agent Skills »)

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/SergeoDev01/talking-head-reels.git \
  ~/.agents/skills/talking-head-reels
```

OpenCode lit aussi `~/.claude/skills` et `~/.agents/skills` en compatibilité. Évitez d'installer le même skill dans plusieurs sources si vous ne voulez pas de doublons d'ID : la source la plus prioritaire gagne.

### 4.4 Dépendances Python

Le plus simple : un venv dans le dossier du skill.

**macOS / Linux**

```bash
cd ~/.config/opencode/skills/talking-head-reels
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy faster-whisper imageio-ffmpeg
```

**Windows PowerShell**

```powershell
cd "$env:USERPROFILE\.config\opencode\skills\talking-head-reels"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install numpy faster-whisper imageio-ffmpeg
```

> Si vous utilisez un venv, l'agent doit exécuter les scripts avec le Python de ce venv. Le plus fiable : activer le venv dans le terminal avant de lancer la session, ou remplacer `python3` par le chemin absolu du Python du venv.

### 4.5 Vérifier l'installation

```bash
cd ~/.config/opencode/skills/talking-head-reels
python3 scripts/check_setup.py
```

Le diagnostic doit être vert (`exit 0`). Sur Windows, le seul avertissement normal restant est `swiftc` (mattes Vision optionnelles).

Dans OpenCode, vérifiez que le skill est visible :

```text
Liste les skills disponibles.
```

Puis chargez-le explicitement avec `@talking-head-reels` dans un prompt (ou laissez le modèle le choisir).

### 4.6 Mettre à jour

```bash
git -C ~/.config/opencode/skills/talking-head-reels pull
```

---

## 5. Installer les MCP utilisés par le skill

Le skill utilise **deux serveurs MCP** et **une API HTTP** :

| Service | Type | Clé API | Usage dans le skill |
|---|---|---|---|
| **Pixabay** | MCP local (`pixabay-mcp`) | **oui**, gratuite | images + vidéos B-roll |
| **thesvg** | MCP local (`@thesvg/mcp-server`) | non | logos et icônes de marques |
| **Wikimedia Commons** | API HTTP via `curl` | non | archives photo/vidéo/audio |

> Les MCP sont des serveurs locaux lancés par votre agent via `npx`. Aucune donnée ne transite par un service tiers autre que Pixabay / thesvg / Wikimedia.

Des fichiers d'exemple prêts à copier sont fournis :

- [`mcp/opencode.jsonc.example`](mcp/opencode.jsonc.example) — bloc `mcp.servers` pour OpenCode V2 ;
- [`mcp/claude.mcp.json.example`](mcp/claude.mcp.json.example) — format `mcpServers` pour Claude Code / Claude Desktop / Cursor.

### 5.1 Installer Node.js

Les deux MCP sont des paquets npm. Installez **Node.js 18+** : <https://nodejs.org/>.

```bash
node --version   # doit afficher v18.x ou plus
npx --version
```

### 5.2 Pixabay — obtenir la clé API (gratuite)

1. Créez un compte gratuit : <https://pixabay.com/accounts/register/>
2. Connectez-vous.
3. Ouvrez la page de documentation de l'API : **<https://pixabay.com/api/docs/>**
4. Votre **clé API** est affichée en haut de la page (format `12345678-1a2b3c4d5e6f7a8b9c0d1e2f`). Copiez-la.
5. La même clé couvre **les images et les vidéos**.

Bon à savoir :

- L'API Pixabay est gratuite. La documentation indique une limite de **100 requêtes / 60 secondes**.
- Ne committez **jamais** la clé dans un dépôt. Utilisez une variable d'environnement.
- Le contenu Pixabay est utilisable gratuitement, y compris commercialement, sous la [Pixabay Content License](https://pixabay.com/service/license-summary/) (pas d'attribution obligatoire, mais certaines restrictions : ne pas revendre le contenu tel quel, etc.).

#### 5.2.1 Connecter Pixabay dans OpenCode

```bash
opencode mcp add pixabay --global \
  --env PIXABAY_API_KEY=COLLEZ_VOTRE_CLE \
  -- npx -y pixabay-mcp@latest
```

Vérifiez :

```bash
opencode mcp list
```

Attendu :

```text
✓ pixabay  connected
```

> **Windows** : si `npx` n'est pas trouvé (erreur `spawn npx ENOENT`), utilisez le lanceur `cmd.exe` :
>
> ```powershell
> opencode mcp add pixabay --global `
>   --env PIXABAY_API_KEY=COLLEZ_VOTRE_CLE `
>   -- cmd.exe /d /c npx -y pixabay-mcp@latest
> ```

#### 5.2.2 Ou configurer Pixabay à la main dans OpenCode

Fichier global : `~/.config/opencode/opencode.jsonc` (Windows : `%USERPROFILE%\.config\opencode\opencode.jsonc`).

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "pixabay": {
        "type": "local",
        "command": ["npx", "-y", "pixabay-mcp@latest"],
        "environment": {
          "PIXABAY_API_KEY": "{env:PIXABAY_API_KEY}"
        }
      }
    }
  }
}
```

Sur Windows, remplacez `command` par :

```jsonc
"command": ["cmd.exe", "/d", "/c", "npx", "-y", "pixabay-mcp@latest"]
```

Puis définissez la variable d'environnement **avant** de lancer OpenCode.

**Windows PowerShell**

```powershell
setx PIXABAY_API_KEY "COLLEZ_VOTRE_CLE"
# rouvrez le terminal
```

**macOS / Linux (zsh)**

```bash
echo 'export PIXABAY_API_KEY="COLLEZ_VOTRE_CLE"' >> ~/.zshrc
source ~/.zshrc
```

Le champ `environment` accepte `{env:NAME}` : OpenCode injecte la variable au processus MCP sans écrire la clé dans le fichier de config.

#### 5.2.3 Connecter Pixabay dans Claude Code

```bash
claude mcp add --env PIXABAY_API_KEY=COLLEZ_VOTRE_CLE \
  --transport stdio pixabay -- npx -y pixabay-mcp@latest
claude mcp list
```

Ou via un fichier `.mcp.json` à la racine de votre projet :

```json
{
  "mcpServers": {
    "pixabay": {
      "command": "npx",
      "args": ["-y", "pixabay-mcp@latest"],
      "env": {
        "PIXABAY_API_KEY": "COLLEZ_VOTRE_CLE"
      }
    }
  }
}
```

Claude Code demande l'approbation du fichier `.mcp.json` au premier lancement (tapez `claude` dans le dossier et acceptez le serveur).

### 5.3 thesvg — logos et icônes (aucune clé)

Le serveur MCP [`@thesvg/mcp-server`](https://www.npmjs.com/package/@thesvg/mcp-server) expose 7 600+ icônes de marques, **sans clé API**.

#### OpenCode

```bash
opencode mcp add thesvg --global -- npx -y @thesvg/mcp-server
opencode mcp list
```

Attendu : `✓ thesvg  connected`.

Configuration manuelle :

```jsonc
{
  "mcp": {
    "servers": {
      "thesvg": {
        "type": "local",
        "command": ["npx", "-y", "@thesvg/mcp-server"]
      }
    }
  }
}
```

Sur Windows, même remarque que Pixabay : `["cmd.exe", "/d", "/c", "npx", "-y", "@thesvg/mcp-server"]`.

#### Claude Code

```bash
claude mcp add --transport stdio thesvg -- npx -y @thesvg/mcp-server
```

Ou dans `.mcp.json` :

```json
{
  "mcpServers": {
    "thesvg": {
      "command": "npx",
      "args": ["-y", "@thesvg/mcp-server"]
    }
  }
}
```

Outils exposés : `search_icons`, `list_variants`, `get_icon_url`, `get_icon`, `list_categories`.

### 5.4 Wikimedia Commons — aucune installation, aucune clé

Wikimedia n'est **pas** un MCP : le skill appelle directement l'API HTTP publique avec `curl`. Il suffit d'une connexion internet et d'un **User-Agent descriptif** pour les téléchargements.

Test rapide :

```bash
curl -s "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=filetype:video%20ocean%20waves&srnamespace=6&srlimit=3&format=json"
```

Téléchargement avec les bons réflexes (le skill le fait) :

```bash
curl -L -o clip.ogv \
  -A "MonProjet/1.0 (contact: vous@example.com)" \
  --retry 4 --retry-delay 8 --retry-all-errors \
  "https://upload.wikimedia.org/..."
```

> Un `User-Agent` absent ou générique peut déclencher un **HTTP 429**. C'est documenté et géré par le skill.

### 5.5 Vérifier que l'agent voit les outils

Dans OpenCode :

```text
/mcps
```

ou demandez simplement :

```text
Cherche 3 vidéos verticales de vagues sur Pixabay et montre-moi les URLs.
```

En **Code Mode** (mode par défaut d'OpenCode V2), les outils sont appelés ainsi :

```js
tools.pixabay.search_pixabay_videos({ query: "ocean waves", orientation: "vertical", per_page: 5 })
tools.thesvg.search_icons({ query: "github" })
```

Sans Code Mode, les noms exposés sont `pixabay_search_pixabay_videos`, `thesvg_search_icons`, etc.

### 5.6 Sécurité de la clé

- La clé Pixabay est **personnelle** : ne la mettez pas dans le dépôt, ni dans un README, ni dans une capture d'écran.
- Préférez `{env:PIXABAY_API_KEY}` dans `opencode.jsonc`.
- En cas de fuite : régénérez la clé depuis <https://pixabay.com/api/docs/>.

---

## 6. Utilisation complète

### 6.1 Le prompt de départ

```text
Utilise le skill @talking-head-reels pour transformer cette vidéo en reel vertical 9:16 :
C:\Users\moi\Videos\interview.mp4

Coupe les pauses et hésitations, sous-titre en français, illustre ce que je dis avec du B-roll
gratuit (Pixabay / Wikimedia), ajoute des gros mots kinétiques et des splits avec moi.
Pas de génération payante. Sortie 1080×1920, audio à −14 LUFS.
```

L'agent charge `SKILL.md`, lit les références, puis travaille.

### 6.2 Ce que l'agent vous demandera (une seule fois)

1. Le chemin de la vidéo (idéalement 4K horizontal ou 1080×1920 vertical, personne centrée).
2. La langue et, si possible, le script (pour corriger les noms mal transcrits).
3. Le grade couleur : fichier déjà étalonné, LUT `.cube`, ou couleurs caméra.
4. Le CTA final (ex. « commente MOT et je t'envoie le lien »).
5. Les droits sur le B-roll : votre matériel, stock libre, logos.
6. Le dossier projet (par défaut : `<nom>_reel/` à côté de la vidéo).

### 6.3 Le pipeline en commandes

Toutes les commandes se lancent depuis le dossier du skill (`~/.config/opencode/skills/talking-head-reels`). `DIR` = dossier projet.

```bash
# 0. Diagnostic
python3 scripts/check_setup.py

# 1. Préparation + transcription + coupe des pauses + mastering
python3 scripts/prepare_project.py VIDEO.mp4 --project DIR
python3 scripts/transcribe.py DIR --language fr --model medium
python3 scripts/cut_pauses.py DIR --remove 12.40-12.92 --remove 33.10-33.55
python3 scripts/master_audio.py DIR

# Mattes de silhouette (macOS + swiftc uniquement)
python3 scripts/presenter_mattes.py DIR

# 2. Écriture de l'EDL (l'agent s'en occupe), puis validation
python3 scripts/validate_edl.py DIR/edl.json

# 3. Stills de contrôle (quelques secondes)
python3 scripts/render_reel.py DIR/edl.json \
  --stills 0.6 2.4 4.8 8.1 12.0 --out-dir DIR/qa/stills_v1

# 4. Rendu complet
python3 scripts/render_reel.py DIR/edl.json --out DIR/render/ma_video_v1.mp4 --workers 6
```

Options utiles :

- `--graded GRADED.mov` ou `--lut grade.cube` sur `prepare_project.py` ;
- `--model small|medium|large-v3` sur `transcribe.py` (plus gros = plus précis, plus lent) ;
- `--remove start-end` en secondes **source** pour retirer les faux départs et tics de langage ;
- `--workers N` pour le rendu (défaut : cœurs − 2, max 8).

### 6.4 Stills, validation, rendu

1. Générez un still au milieu de **chaque beat** + au milieu de chaque transition.
2. Vérifiez avec la checklist de `references/style-guide.md` :
   - pas de bords vides ou noirs ;
   - textes lisibles et dans le cadre ;
   - rien sur les yeux ;
   - texte dans la pile centrale ;
   - traitement couleur correct.
3. Corrigez l'EDL et recommencez jusqu'à un résultat propre.
4. Lancez le rendu complet : quelques minutes sur un Mac récent, davantage sur Windows.

### 6.5 Révisions

- Envoyez vos notes **une par une** (souvent des captures + quelques mots). L'agent les numérote et n'applique rien tant que vous n'avez pas dit « c'est bon / go ».
- Chaque round crée une **nouvelle version** : `edl_v2.json`, `ma_video_v2.mp4`. Aucun rendu déjà vu n'est écrasé.
- Une note générale (« pas de bords vides », « sous-titres plus gros ») s'applique **partout**, pas seulement sur la capture.

### 6.6 Sorties

```text
DIR/
├── edl.json                 # le montage complet, reproductible
├── edl_v2.json              # versions suivantes
├── analysis/
│   ├── program_words.json   # mots + temps programme
│   └── ...
├── broll/                   # clips sourcés
├── logos/                   # PNG transparents
├── qa/stills_v1/sheet.jpg   # planche de contrôle
├── render/
│   └── ma_video_v1.mp4      # 1080×1920, H.264, AAC
└── CREDITS.md               # sources + licences (à tenir à jour)
```

---

## Démo (avant/après)

Voici un exemple concret de ce que le skill produit, à partir d'une vidéo source face caméra.

| | Fichier | Description |
|---|---|---|
| **Avant (source)** | [`assets/demos/original.mp4`](assets/demos/original.mp4) | Vidéo originale brute (face caméra, pauses et hésitations incluses) |
| **Après (skill)** | [`assets/demos/result.mp4`](assets/demos/result.mp4) | Reel 9:16 rendu par le skill : pauses coupées, sous-titres kinétiques, B-roll, splits, audio masterisé à −14 LUFS |

**Spécifications du rendu :**

- Format : 1080×1920 (9:16 vertical)
- Codec : H.264 (CRF 12, yuv420p, BT.709)
- Audio : AAC 320 kbps 48 kHz, `+faststart`, voix ~−14 LUFS

> Les deux fichiers sont fournis à titre d'exemple dans le dépôt. Ce ne sont pas des sorties des scripts du skill : ce sont des références pour voir le rendu attendu.

---

## 7. Structure du dépôt

```text
talking-head-reels/
├── SKILL.md                     # instructions chargées par l'agent
├── README.md                    # ce fichier
├── LICENSE                      # MIT
├── THIRD_PARTY.md               # licences des composants tiers
├── .gitignore
├── assets/
│   ├── examples/example_edl.json
│   ├── fonts/                   # Anton (OFL) + OFL.txt
│   ├── fonts/win/               # Playfair Display + Inter (OFL)
│   └── textures/halftone_1080x1920.png
├── references/
│   ├── broll-sourcing.md        # recettes Pixabay / Wikimedia / thesvg testées
│   ├── edit-planning.md         # transformer un discours en beats
│   ├── edl-schema.md            # schéma complet de l'EDL
│   ├── renderer.md              # fonctionnement du rendu, polices, vitesse
│   └── style-guide.md           # le look et les règles
└── scripts/
    ├── check_setup.py
    ├── prepare_project.py
    ├── transcribe.py
    ├── cut_pauses.py
    ├── master_audio.py
    ├── presenter_mattes.py
    ├── clip_sheet.py
    ├── clip_matte.py
    ├── validate_edl.py
    ├── render_reel.py
    ├── reel_plan.py
    ├── textass.py
    ├── fontmetrics.py
    ├── common.py
    └── vision/                  # Swift Apple Vision (optionnel)
```

---

## 8. Sources gratuites, licences et attribution

### 8.1 D'où vient le contenu

Ordre de préférence appliqué par le skill :

1. **Votre matériel** (autres rushes, captures d'écran, photos produit).
2. **Stock et archives libres** : Pixabay (MCP), Wikimedia Commons (API), thesvg (MCP) pour les logos.
3. **Matériel licencié** que vous avez le droit d'utiliser.
4. **Génération IA payante** (Higgsfield / Seedance) : uniquement sur demande explicite et après accord sur le coût (appendice de `references/broll-sourcing.md`).

### 8.2 Licences des sources

| Source | Licence | Attribution |
|---|---|---|
| Pixabay | [Pixabay Content License](https://pixabay.com/service/license-summary/) | non obligatoire |
| Wikimedia Commons | **variable selon le fichier** (domaine public, CC BY, CC BY-SA…) | selon le fichier — à consigner |
| thesvg | code **MIT** ; les logos sont des **marques déposées** de leurs propriétaires | usage d'identification ; vérifier la marque |
| Polices Anton / Playfair Display / Inter | **SIL Open Font License 1.1** | conservation des fichiers OFL |
| ffmpeg | LGPL / GPL selon le build | selon le build |
| faster-whisper | MIT | — |
| numpy | BSD-3-Clause | — |

Le skill tient un fichier `PROJECT/CREDITS.md` : **fichier → URL source → licence → auteur**. Gardez-le avec le projet, surtout pour Wikimedia.

### 8.3 Fichiers open source utilisés

- **Anton** — <https://github.com/google/fonts/tree/main/ofl/anton> (OFL 1.1)
- **Playfair Display** — <https://github.com/google/fonts/tree/main/ofl/playfairdisplay> (OFL 1.1)
- **Inter** — <https://github.com/rsms/inter> (OFL 1.1)
- **pixabay-mcp** — <https://github.com/zym9863/pixabay-mcp> (MIT)
- **thesvg** — <https://github.com/glincker/thesvg> (MIT pour le code)
- **ffmpeg** — <https://ffmpeg.org/> (LGPL/GPL)
- **faster-whisper** — <https://github.com/SYSTRAN/faster-whisper> (MIT)

Les fichiers de licence d'origine sont conservés dans `assets/fonts/` et `assets/fonts/win/`. Voir aussi [THIRD_PARTY.md](THIRD_PARTY.md).

### 8.4 Génération payante (optionnelle)

L'appendice A de `references/broll-sourcing.md` documente Seedance via Higgsfield. Il n'est **pas** utilisé par défaut, ne contient aucune clé, et nécessite un compte + des crédits. Le skill ne l'ouvre que si vous demandez explicitement des plans générés par IA et que vous approuvez le coût.

---

## 9. Dépannage

| Symptôme | Cause / solution |
|---|---|
| `python3: command not found` (Windows) | Utilisez `python` ou `py -3`. |
| `check_setup.py` : ffmpeg sans libass | Installez un build avec libass : `brew install ffmpeg` (macOS) ou le build « full » gyan.dev (Windows). |
| Texte absent sur toutes les frames | ffmpeg sans libass, ou police introuvable. Relancez `check_setup.py` et cherchez `fonts not found for libass` dans le log. |
| Texte dans une police par défaut | Le nom PostScript est faux. Sur Windows, utilisez `PlayfairDisplay-Bold`, `PlayfairDisplay-Regular`, `Inter-Medium` et l'override `fonts` dans l'EDL. |
| `REEL_FONT_FILES` ignoré | La variable n'est lue que par les **nouveaux** processus : rouvrez le terminal. |
| `swiftc` absent | Normal sur Windows. Les mattes Vision sont sautées ; le reste fonctionne. |
| `spawn npx ENOENT` (MCP, Windows) | Utilisez `cmd.exe /d /c npx ...` dans la config MCP. |
| `opencode mcp list` : `pixabay failed` | Vérifiez `node -v`, la clé `PIXABAY_API_KEY`, puis lancez `npx -y pixabay-mcp@latest` à la main pour voir l'erreur. |
| Pixabay `400` | Clé invalide ou paramètre hors bornes (`per_page` 3–200). |
| Pixabay `429` | Limite de 100 requêtes / 60 s atteinte : attendez. |
| Les outils MCP n'apparaissent pas | `/mcps`, puis `opencode service restart` si le service est bloqué. |
| Rendu très long | Normal : quelques minutes pour ~75 s. Utilisez `--workers`, et rendez d'abord les stills. |
| `__pycache__` dans le dossier | Créé par Python à l'exécution, ignoré par Git. Supprimable sans risque. |
| Bords noirs dans un still | Clip trop petit pour son mouvement : augmentez `zoom`, vérifiez `fx`. |
| Sous-titres décalés | Relancez `transcribe.py` avec un modèle plus gros, ou ajustez `wt` à la main. |

---

## 10. FAQ

**Faut-il After Effects ou Premiere ?**
Non. Tout est rendu par Python + ffmpeg/libass. Aucun logiciel de montage n'est requis.

**Est-ce que ça marche sur Windows ?**
Oui pour le rendu. Les mattes Apple Vision (silhouettes) sont macOS uniquement et simplement ignorées sur Windows. Les polices libres fournies remplacent Didot / Helvetica Neue.

**Est-ce vraiment gratuit ?**
Oui : Pixabay, Wikimedia et thesvg sont gratuits. La génération IA payante est un appendice désactivé par défaut.

**Puis-je utiliser mes propres rushes ?**
Oui, c'est même la première source préférée. Le skill ne re-source pas ce que vous fournissez.

**Où est stockée la clé Pixabay ?**
Dans la config MCP (`opencode.jsonc` ou `.mcp.json`) ou, mieux, dans une variable d'environnement via `{env:PIXABAY_API_KEY}`.

**Comment mettre à jour le skill ?**
`git -C ~/.config/opencode/skills/talking-head-reels pull`, puis `pip install -r` si les dépendances changent.

**Le skill parle français ?**
Les fichiers de projet et le code sont en anglais ; l'agent vous parle dans votre langue et les sous-titres sont dans la langue de la vidéo.

---

## 11. Licence

Le code et la documentation de ce dépôt sont sous **MIT** — voir [LICENSE](LICENSE).

Les polices, icônes, médias et autres composants tiers restent sous leurs licences respectives (voir [THIRD_PARTY.md](THIRD_PARTY.md) et les fichiers `OFL.txt`). Les logos de marques appartiennent à leurs propriétaires.

---

**Dépôt :** <https://github.com/SergeoDev01/talking-head-reels>
**Skill associé :** [voiceover-glass-reel](https://github.com/SergeoDev01/voiceover-glass-reel)
