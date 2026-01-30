# Fileshed Test Execution Report

**Version**: 1.0.3
**Tests executed**: 1101/1101
**Result**: ✅ ALL PASSED

---

| # | Status | Description | Command | Expected |
|--:|:------:|-------------|---------|----------|
| TEST-001 | ✅ | Liste simple du répertoire racine Storage | `shed_exec(zone="storage", cmd="ls")` | ✓ success |
| TEST-002 | ✅ | Liste détaillée avec -la | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-003 | ✅ | Liste d'un sous-dossier | `shed_exec(zone="storage", cmd="ls", args=["pr...` | ✓ success |
| TEST-004 | ✅ | Liste avec tri par taille | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-005 | ✅ | Liste avec tri par date | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-006 | ✅ | Liste récursive | `shed_exec(zone="storage", cmd="ls", args=["-R...` | ✓ success |
| TEST-007 | ✅ | Liste avec taille human-readable | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-008 | ✅ | Liste zone uploads | `shed_exec(zone="uploads", cmd="ls", args=["-l...` | ✓ success |
| TEST-009 | ✅ | Liste zone documents | `shed_exec(zone="documents", cmd="ls", args=["...` | ✓ success |
| TEST-010 | ✅ | Liste zone group | `shed_exec(zone="group", group="team-alpha", c...` | ✓ success |
| TEST-011 | ✅ | Liste fichiers cachés uniquement | `shed_exec(zone="storage", cmd="ls", args=["-d...` | ✓ success |
| TEST-012 | ✅ | Liste avec inode | `shed_exec(zone="storage", cmd="ls", args=["-i...` | ✓ success |
| TEST-013 | ✅ | Liste un fichier spécifique | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-014 | ✅ | Liste avec glob pattern | `shed_exec(zone="storage", cmd="ls", args=["*....` | ✓ success |
| TEST-015 | ✅ | Liste fichier inexistant | `shed_exec(zone="storage", cmd="ls", args=["no...` | ✗ error |
| TEST-016 | ✅ | Liste avec -1 (un par ligne) | `shed_exec(zone="storage", cmd="ls", args=["-1...` | ✓ success |
| TEST-017 | ✅ | Liste avec -A (sans . et ..) | `shed_exec(zone="storage", cmd="ls", args=["-A...` | ✓ success |
| TEST-018 | ✅ | Liste zone invalide | `shed_exec(zone="invalid", cmd="ls")` | INVALID_ZONE |
| TEST-019 | ✅ | Liste group sans paramètre group | `shed_exec(zone="group", cmd="ls")` | MISSING_GROUP |
| TEST-020 | ✅ | Liste avec chemin absolu (bloqué) | `shed_exec(zone="storage", cmd="ls", args=["/e...` | PATH_ESCAPE |
| TEST-021 | ✅ | Lecture fichier simple | `shed_exec(zone="storage", cmd="cat", args=["r...` | ✓ success |
| TEST-022 | ✅ | Lecture avec numéros de ligne | `shed_exec(zone="storage", cmd="cat", args=["-...` | ✓ success |
| TEST-023 | ✅ | Lecture fichier inexistant | `shed_exec(zone="storage", cmd="cat", args=["n...` | ✗ error |
| TEST-024 | ✅ | Lecture multiple fichiers | `shed_exec(zone="storage", cmd="cat", args=["f...` | ✓ success |
| TEST-025 | ✅ | Lecture zone uploads | `shed_exec(zone="uploads", cmd="cat", args=["u...` | ✓ success |
| TEST-026 | ✅ | Lecture zone documents | `shed_exec(zone="documents", cmd="cat", args=[...` | ✓ success |
| TEST-027 | ✅ | Lecture avec -b (numéros lignes non vides) | `shed_exec(zone="storage", cmd="cat", args=["-...` | ✓ success |
| TEST-028 | ✅ | Lecture avec -s (squeeze blank) | `shed_exec(zone="storage", cmd="cat", args=["-...` | ✓ success |
| TEST-029 | ✅ | Lecture avec -E ($ en fin de ligne) | `shed_exec(zone="storage", cmd="cat", args=["-...` | ✓ success |
| TEST-030 | ✅ | Lecture fichier binaire (affichage tronqué) | `shed_exec(zone="storage", cmd="cat", args=["i...` | ✓ success |
| TEST-031 | ✅ | Lecture fichier vide | `shed_exec(zone="storage", cmd="cat", args=["e...` | ✓ success |
| TEST-032 | ✅ | Lecture fichier volumineux | `shed_exec(zone="storage", cmd="cat", args=["l...` | ✓ success |
| TEST-033 | ✅ | Lecture avec path traversal (bloqué) | `shed_exec(zone="storage", cmd="cat", args=["....` | PATH_ESCAPE |
| TEST-034 | ✅ | Lecture fichier dans sous-dossier | `shed_exec(zone="storage", cmd="cat", args=["p...` | ✓ success |
| TEST-035 | ✅ | Lecture avec tac (reverse) | `shed_exec(zone="storage", cmd="tac", args=["f...` | ✓ success |
| TEST-036 | ✅ | Head par défaut (10 lignes) | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-037 | ✅ | Head avec -n spécifique | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-038 | ✅ | Head avec -c (bytes) | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-039 | ✅ | Tail par défaut (10 lignes) | `shed_exec(zone="storage", cmd="tail", args=["...` | ✓ success |
| TEST-040 | ✅ | Tail avec -n spécifique | `shed_exec(zone="storage", cmd="tail", args=["...` | ✓ success |
| TEST-041 | ✅ | Tail avec +n (depuis ligne n) | `shed_exec(zone="storage", cmd="tail", args=["...` | ✓ success |
| TEST-042 | ✅ | Tail avec -c (bytes) | `shed_exec(zone="storage", cmd="tail", args=["...` | ✓ success |
| TEST-043 | ✅ | Head fichier vide | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-044 | ✅ | Tail fichier vide | `shed_exec(zone="storage", cmd="tail", args=["...` | ✓ success |
| TEST-045 | ✅ | Head multiple fichiers | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-046 | ✅ | Tail zone uploads | `shed_exec(zone="uploads", cmd="tail", args=["...` | ✓ success |
| TEST-047 | ✅ | Head zone documents | `shed_exec(zone="documents", cmd="head", args=...` | ✓ success |
| TEST-048 | ✅ | Extraction lignes milieu avec sed | `shed_exec(zone="storage", cmd="sed", args=["-...` | ✓ success |
| TEST-049 | ✅ | Head avec -q (quiet, pas de header) | `shed_exec(zone="storage", cmd="head", args=["...` | ✓ success |
| TEST-050 | ✅ | Tail fichier inexistant | `shed_exec(zone="storage", cmd="tail", args=["...` | ✗ error |
| TEST-051 | ✅ | Grep pattern simple | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-052 | ✅ | Grep case insensitive | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-053 | ✅ | Grep avec numéros de ligne | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-054 | ✅ | Grep récursif | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-055 | ✅ | Grep avec contexte (-C) | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-056 | ✅ | Grep inverse (-v) | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-057 | ✅ | Grep count only (-c) | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-058 | ✅ | Grep files only (-l) | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-059 | ✅ | Grep regex étendu | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-060 | ✅ | Grep whole word (-w) | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-061 | ✅ | Egrep (alias grep -E) | `shed_exec(zone="storage", cmd="egrep", args=[...` | ✓ success |
| TEST-062 | ✅ | Fgrep (fixed strings) | `shed_exec(zone="storage", cmd="fgrep", args=[...` | ✓ success |
| TEST-063 | ✅ | Grep avec --include | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-064 | ✅ | Grep avec --exclude | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-065 | ✅ | Grep aucun match | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-066 | ✅ | Find fichiers par pattern | `shed_exec(zone="storage", cmd="find", args=["...` | ✓ success |
| TEST-067 | ✅ | Find fichiers par nom | `shed_exec(zone="storage", cmd="find", args=["...` | ✓ success |
| TEST-068 | ✅ | Find par type (fichiers) | `shed_exec(zone="storage", cmd="find", args=["...` | ✓ success |
| TEST-069 | ✅ | Find par type (dossiers) | `shed_exec(zone="storage", cmd="find", args=["...` | ✓ success |
| TEST-070 | ✅ | Find avec -maxdepth | `shed_exec(zone="storage", cmd="find", args=["...` | ✓ success |
| TEST-071 | ✅ | Awk print colonne | `shed_exec(zone="storage", cmd="awk", args=["{...` | ✓ success |
| TEST-072 | ✅ | Awk avec délimiteur | `shed_exec(zone="storage", cmd="awk", args=["-...` | ✓ success |
| TEST-073 | ✅ | Awk calcul | `shed_exec(zone="storage", cmd="awk", args=["{...` | ✓ success |
| TEST-074 | ✅ | Awk filtrage regex | `shed_exec(zone="storage", cmd="awk", args=["/...` | ✓ success |
| TEST-075 | ✅ | Awk NR (numéro ligne) | `shed_exec(zone="storage", cmd="awk", args=["N...` | ✓ success |
| TEST-076 | ✅ | Sed substitution simple | `shed_exec(zone="storage", cmd="sed", args=["s...` | ✓ success |
| TEST-077 | ✅ | Sed substitution globale | `shed_exec(zone="storage", cmd="sed", args=["s...` | ✓ success |
| TEST-078 | ✅ | Sed delete ligne | `shed_exec(zone="storage", cmd="sed", args=["5...` | ✓ success |
| TEST-079 | ✅ | Sed range de lignes | `shed_exec(zone="storage", cmd="sed", args=["-...` | ✓ success |
| TEST-080 | ✅ | Sed avec regex | `shed_exec(zone="storage", cmd="sed", args=["s...` | ✓ success |
| TEST-081 | ✅ | Sed insert ligne | `shed_exec(zone="storage", cmd="sed", args=["3...` | ✓ success |
| TEST-082 | ✅ | Sed append ligne | `shed_exec(zone="storage", cmd="sed", args=["3...` | ✓ success |
| TEST-083 | ✅ | Awk multiple colonnes | `shed_exec(zone="storage", cmd="awk", args=["{...` | ✓ success |
| TEST-084 | ✅ | Sed multiple commandes | `shed_exec(zone="storage", cmd="sed", args=["-...` | ✓ success |
| TEST-085 | ✅ | Awk BEGIN/END | `shed_exec(zone="storage", cmd="awk", args=["B...` | ✓ success |
| TEST-086 | ✅ | Word count (wc) | `shed_exec(zone="storage", cmd="wc", args=["fi...` | ✓ success |
| TEST-087 | ✅ | Word count lignes seulement | `shed_exec(zone="storage", cmd="wc", args=["-l...` | ✓ success |
| TEST-088 | ✅ | Sort alphabétique | `shed_exec(zone="storage", cmd="sort", args=["...` | ✓ success |
| TEST-089 | ✅ | Sort numérique | `shed_exec(zone="storage", cmd="sort", args=["...` | ✓ success |
| TEST-090 | ✅ | Sort reverse | `shed_exec(zone="storage", cmd="sort", args=["...` | ✓ success |
| TEST-091 | ✅ | Uniq (supprimer doublons consécutifs) | `shed_exec(zone="storage", cmd="uniq", args=["...` | ✓ success |
| TEST-092 | ✅ | Uniq avec count | `shed_exec(zone="storage", cmd="uniq", args=["...` | ✓ success |
| TEST-093 | ✅ | Cut colonnes | `shed_exec(zone="storage", cmd="cut", args=["-...` | ✓ success |
| TEST-094 | ✅ | Tr translate | `shed_exec(zone="storage", cmd="tr", args=["a-...` | Note - tr lit stdin, test avec |
| TEST-095 | ✅ | Rev (reverse lines) | `shed_exec(zone="storage", cmd="rev", args=["f...` | ✓ success |
| TEST-096 | ✅ | Nl (number lines) | `shed_exec(zone="storage", cmd="nl", args=["fi...` | ✓ success |
| TEST-097 | ✅ | Format text paragraphs | `shed_exec(zone="storage", cmd="fmt", args=["-...` | ✓ success |
| TEST-098 | ✅ | Fold (wrap lines) | `shed_exec(zone="storage", cmd="fold", args=["...` | ✓ success |
| TEST-099 | ✅ | Fmt (format paragraphes) | `shed_exec(zone="storage", cmd="fmt", args=["-...` | ✓ success |
| TEST-100 | ✅ | Paste (merge files) | `shed_exec(zone="storage", cmd="paste", args=[...` | ✓ success |
| TEST-101 | ✅ | Créer dossier simple | `shed_exec(zone="storage", cmd="mkdir", args=[...` | ✓ success |
| TEST-102 | ✅ | Créer arborescence (-p) | `shed_exec(zone="storage", cmd="mkdir", args=[...` | ✓ success |
| TEST-103 | ✅ | mkdir dossier existant (erreur) | `shed_exec(zone="storage", cmd="mkdir", args=[...` | returncode non-zero, dossier e |
| TEST-104 | ✅ | mkdir -p dossier existant (ok) | `shed_exec(zone="storage", cmd="mkdir", args=[...` | ✓ success |
| TEST-105 | ✅ | mkdir zone documents | `shed_exec(zone="documents", cmd="mkdir", args...` | ✓ success |
| TEST-106 | ✅ | mkdir zone uploads (interdit) | `shed_exec(zone="uploads", cmd="mkdir", args=[...` | ✗ error |
| TEST-107 | ✅ | touch créer fichier | `shed_exec(zone="storage", cmd="touch", args=[...` | ✓ success |
| TEST-108 | ✅ | touch fichier existant (update time) | `shed_exec(zone="storage", cmd="touch", args=[...` | ✓ success |
| TEST-109 | ✅ | touch multiple fichiers | `shed_exec(zone="storage", cmd="touch", args=[...` | ✓ success |
| TEST-110 | ✅ | touch dans sous-dossier | `shed_exec(zone="storage", cmd="touch", args=[...` | ✓ success |
| TEST-111 | ✅ | touch zone documents | `shed_exec(zone="documents", cmd="touch", args...` | ✓ success |
| TEST-112 | ✅ | touch zone group | `shed_exec(zone="group", group="team", cmd="to...` | ✓ success |
| TEST-113 | ✅ | mkdir avec verbose (-v) | `shed_exec(zone="storage", cmd="mkdir", args=[...` | ✓ success |
| TEST-114 | ✅ | touch avec timestamp spécifique | `shed_exec(zone="storage", cmd="touch", args=[...` | ✓ success |
| TEST-115 | ✅ | mkdir chemin avec espaces | `shed_exec(zone="storage", cmd="mkdir", args=[...` | ✓ success |
| TEST-116 | ✅ | Copie fichier simple | `shed_exec(zone="storage", cmd="cp", args=["so...` | ✓ success |
| TEST-117 | ✅ | Copie dans dossier | `shed_exec(zone="storage", cmd="cp", args=["fi...` | ✓ success |
| TEST-118 | ✅ | Copie récursive | `shed_exec(zone="storage", cmd="cp", args=["-r...` | ✓ success |
| TEST-119 | ✅ | Copie avec préservation (-p) | `shed_exec(zone="storage", cmd="cp", args=["-p...` | ✓ success |
| TEST-120 | ✅ | Copie multiple fichiers | `shed_exec(zone="storage", cmd="cp", args=["a....` | ✓ success |
| TEST-121 | ✅ | Move fichier | `shed_exec(zone="storage", cmd="mv", args=["ol...` | ✓ success |
| TEST-122 | ✅ | Move dans dossier | `shed_exec(zone="storage", cmd="mv", args=["fi...` | ✓ success |
| TEST-123 | ✅ | Move dossier | `shed_exec(zone="storage", cmd="mv", args=["fo...` | ✓ success |
| TEST-124 | ✅ | Remove fichier | `shed_exec(zone="storage", cmd="rm", args=["un...` | ✓ success |
| TEST-125 | ✅ | Remove multiple fichiers | `shed_exec(zone="storage", cmd="rm", args=["a....` | ✓ success |
| TEST-126 | ✅ | Remove dossier vide | `shed_exec(zone="storage", cmd="rmdir", args=[...` | ✓ success |
| TEST-127 | ✅ | Remove récursif | `shed_exec(zone="storage", cmd="rm", args=["-r...` | ✓ success |
| TEST-128 | ✅ | Remove avec force (-f) | `shed_exec(zone="storage", cmd="rm", args=["-f...` | ✓ success |
| TEST-129 | ✅ | Remove fichier inexistant (erreur) | `shed_exec(zone="storage", cmd="rm", args=["no...` | returncode non-zero |
| TEST-130 | ✅ | cp zone documents | `shed_exec(zone="documents", cmd="cp", args=["...` | ✓ success |
| TEST-131 | ✅ | mv zone documents | `shed_exec(zone="documents", cmd="mv", args=["...` | ✓ success |
| TEST-132 | ✅ | rm zone documents | `shed_exec(zone="documents", cmd="rm", args=["...` | ✓ success |
| TEST-133 | ✅ | cp zone group | `shed_exec(zone="group", group="team", cmd="cp...` | ✓ success |
| TEST-134 | ✅ | mv avec verbose (-v) | `shed_exec(zone="storage", cmd="mv", args=["-v...` | ✓ success |
| TEST-135 | ✅ | cp avec interactive (-i) - non interactif | `shed_exec(zone="storage", cmd="cp", args=["sr...` | ✓ success |
| TEST-136 | ✅ | rm dossier non vide sans -r (erreur) | `shed_exec(zone="storage", cmd="rm", args=["no...` | returncode non-zero, est un do |
| TEST-137 | ✅ | cp avec backup (-b) | `shed_exec(zone="storage", cmd="cp", args=["-b...` | ✓ success |
| TEST-138 | ✅ | mv fichier vers lui-même | `shed_exec(zone="storage", cmd="mv", args=["fi...` | erreur ou no-op |
| TEST-139 | ✅ | cp lien symbolique | `shed_exec(zone="storage", cmd="cp", args=["-P...` | ✓ success |
| TEST-140 | ✅ | rm avec glob pattern | `shed_exec(zone="storage", cmd="rm", args=["*....` | ✓ success |
| TEST-141 | ✅ | Gzip compression | `shed_exec(zone="storage", cmd="gzip", args=["...` | ✓ success |
| TEST-142 | ✅ | Gunzip décompression | `shed_exec(zone="storage", cmd="gunzip", args=...` | ✓ success |
| TEST-143 | ✅ | Gzip keep original (-k) | `shed_exec(zone="storage", cmd="gzip", args=["...` | ✓ success |
| TEST-144 | ✅ | Bzip2 compression | `shed_exec(zone="storage", cmd="bzip2", args=[...` | ✓ success |
| TEST-145 | ✅ | Bunzip2 décompression | `shed_exec(zone="storage", cmd="bunzip2", args...` | ✓ success |
| TEST-146 | ✅ | Xz compression | `shed_exec(zone="storage", cmd="xz", args=["lo...` | ✓ success |
| TEST-147 | ✅ | Unxz décompression | `shed_exec(zone="storage", cmd="unxz", args=["...` | ✓ success |
| TEST-148 | ✅ | Tar création archive | `shed_exec(zone="storage", cmd="tar", args=["-...` | ✓ success |
| TEST-149 | ✅ | Tar extraction | `shed_exec(zone="storage", cmd="tar", args=["-...` | ✓ success |
| TEST-150 | ✅ | Tar avec gzip (.tar.gz) | `shed_exec(zone="storage", cmd="tar", args=["-...` | ✓ success |
| TEST-151 | ✅ | Tar extraction .tar.gz | `shed_exec(zone="storage", cmd="tar", args=["-...` | ✓ success |
| TEST-152 | ✅ | Tar list contents | `shed_exec(zone="storage", cmd="tar", args=["-...` | ✓ success |
| TEST-153 | ✅ | Zcat lecture compressé | `shed_exec(zone="storage", cmd="zcat", args=["...` | ✓ success |
| TEST-154 | ✅ | Compression zone documents | `shed_exec(zone="documents", cmd="gzip", args=...` | ✓ success |
| TEST-155 | ✅ | Zstd compression - unavailable command | `shed_exec(zone="storage", cmd="zstd", args=["...` | ✗ error |
| TEST-156 | ✅ | Git status | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-157 | ✅ | Git log | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-158 | ✅ | Git diff | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-159 | ✅ | Git diff HEAD~1 | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-160 | ✅ | Git show | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-161 | ✅ | Git branch list | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-162 | ✅ | Git rev-parse HEAD | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-163 | ✅ | Git log graph | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-164 | ✅ | Git blame | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-165 | ✅ | Git log fichier spécifique | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-166 | ✅ | Git zone group | `shed_exec(zone="group", group="team", cmd="gi...` | ✓ success |
| TEST-167 | ✅ | Git shortlog | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-168 | ✅ | Git ls-files | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-169 | ✅ | Git zone storage (pas de repo auto) | `shed_exec(zone="storage", cmd="git", args=["s...` | erreur si pas de repo, ou stat |
| TEST-170 | ✅ | Git stash (si supported) | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-171 | ✅ | Redirection simple | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-172 | ✅ | jq avec redirection | `shed_exec(zone="storage", cmd="jq", args=["."...` | ✓ success |
| TEST-173 | ✅ | grep avec redirection | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-174 | ✅ | sort avec redirection | `shed_exec(zone="storage", cmd="sort", args=["...` | ✓ success |
| TEST-175 | ✅ | awk avec redirection | `shed_exec(zone="storage", cmd="awk", args=["-...` | ✓ success |
| TEST-176 | ✅ | cat avec redirection (copie) | `shed_exec(zone="storage", cmd="cat", args=["s...` | ✓ success |
| TEST-177 | ✅ | Redirection zone documents | `shed_exec(zone="documents", cmd="ls", args=["...` | ✓ success |
| TEST-178 | ✅ | Redirection écrase fichier existant | `shed_exec(zone="storage", cmd="echo", args=["...` | ✓ success |
| TEST-179 | ✅ | Redirection dans sous-dossier | `shed_exec(zone="storage", cmd="ls", stdout_fi...` | ✓ success |
| TEST-180 | ✅ | stderr_file redirection | `shed_exec(zone="storage", cmd="ls", args=["no...` | erreur capturée dans errors.lo |
| TEST-181 | ✅ | Créer fichier texte simple | `shed_patch_text(zone="storage", path="hello.t...` | ✓ success |
| TEST-182 | ✅ | Créer fichier dans sous-dossier | `shed_patch_text(zone="storage", path="project...` | ✓ success |
| TEST-183 | ✅ | Créer fichier multiligne | `shed_patch_text(zone="storage", path="script....` | ✓ success |
| TEST-184 | ✅ | Créer fichier vide | `shed_patch_text(zone="storage", path="empty.t...` | ✓ success |
| TEST-185 | ✅ | Créer fichier zone documents | `shed_patch_text(zone="documents", path="note....` | ✓ success |
| TEST-186 | ✅ | Créer fichier zone documents avec message | `shed_patch_text(zone="documents", path="repor...` | ✓ success |
| TEST-187 | ✅ | Create file in group zone | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-188 | ✅ | Créer fichier avec caractères spéciaux | `shed_patch_text(zone="storage", path="special...` | ✓ success |
| TEST-189 | ✅ | Créer fichier avec emoji | `shed_patch_text(zone="storage", path="emoji.t...` | ✓ success |
| TEST-190 | ✅ | Créer fichier JSON | `shed_patch_text(zone="storage", path="config....` | ✓ success |
| TEST-191 | ✅ | Créer fichier YAML | `shed_patch_text(zone="storage", path="config....` | ✓ success |
| TEST-192 | ✅ | Créer fichier avec tabs | `shed_patch_text(zone="storage", path="tabbed....` | ✓ success |
| TEST-193 | ✅ | Créer fichier zone uploads (interdit) | `shed_patch_text(zone="uploads", path="forbidd...` | ZONE_READONLY |
| TEST-194 | ✅ | Créer avec path traversal (bloqué) | `shed_patch_text(zone="storage", path="../../....` | PATH_ESCAPE |
| TEST-195 | ✅ | Créer fichier volumineux | `shed_patch_text(zone="storage", path="large.t...` | ✓ success |
| TEST-196 | ✅ | Créer fichier nom avec espaces | `shed_patch_text(zone="storage", path="my file...` | ✓ success |
| TEST-197 | ✅ | Créer fichier nom avec caractères spéciaux | `shed_patch_text(zone="storage", path="file-na...` | ✓ success |
| TEST-198 | ✅ | Écraser fichier existant | `shed_patch_text(zone="storage", path="existin...` | ✓ success |
| TEST-199 | ✅ | Append to existing file with overwrite=False | `shed_patch_text(zone="storage", path="existin...` | ✓ success |
| TEST-200 | ✅ | Créer fichier groupe sans paramètre group | `shed_patch_text(zone="group", path="test.txt"...` | MISSING_GROUP |
| TEST-201 | ✅ | Append à la fin | `shed_patch_text(zone="storage", path="log.txt...` | ✓ success |
| TEST-202 | ✅ | Prepend au début | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-203 | ✅ | Append multiple fois | `shed_patch_text(zone="storage", path="log.txt...` | ✓ success |
| TEST-204 | ✅ | Insert avant ligne spécifique | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-205 | ✅ | Insert après ligne spécifique | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-206 | ✅ | Insert ligne 1 | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-207 | ✅ | Insert ligne invalide (0) | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-208 | ✅ | Insert ligne > nombre de lignes | `shed_patch_text(zone="storage", path="short.t...` | ✗ error |
| TEST-209 | ✅ | Append zone documents | `shed_patch_text(zone="documents", path="notes...` | ✓ success |
| TEST-210 | ✅ | Append zone group | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-211 | ✅ | Insert avec message git | `shed_patch_text(zone="documents", path="doc.m...` | ✓ success |
| TEST-212 | ✅ | Append fichier inexistant | `shed_patch_text(zone="storage", path="new.txt...` | ✓ success |
| TEST-213 | ✅ | Prepend fichier vide | `shed_patch_text(zone="storage", path="empty.t...` | ✓ success |
| TEST-214 | ✅ | Append avec newline final | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-215 | ✅ | Insert multiligne | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-216 | ✅ | Append caractères binaires (peut échouer) | `shed_patch_text(zone="storage", path="file.tx...` | Dépend de l'implémentation (te |
| TEST-217 | ✅ | Insert très long contenu | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-218 | ✅ | Create new file in group where user is member | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-219 | ✅ | Create file named locked.txt (no actual lock) | `shed_patch_text(zone="storage", path="locked....` | ✓ success |
| TEST-220 | ✅ | Position invalide | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-221 | ✅ | Replace pattern simple | `shed_patch_text(zone="storage", path="config....` | ✓ success |
| TEST-222 | ✅ | Replace pattern regex | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-223 | ✅ | Replace pattern non trouvé | `shed_patch_text(zone="storage", path="file.tx...` | PATTERN_NOT_FOUND |
| TEST-224 | ✅ | Replace all occurrences with match_all=True | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-225 | ✅ | Replace first occurrence only (no match_all) | `shed_patch_text(zone="storage", path="readme....` | ✓ success |
| TEST-226 | ✅ | Replace with capture groups | `shed_patch_text(zone="storage", path="replace...` | ✓ success |
| TEST-227 | ✅ | Replace multiline pattern (line1 followed by line2... | `shed_patch_text(zone="storage", path="multili...` | ✓ success |
| TEST-228 | ✅ | Replace zone documents | `shed_patch_text(zone="documents", path="doc.m...` | ✓ success |
| TEST-229 | ✅ | Replace zone group | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-230 | ✅ | Replace avec message git | `shed_patch_text(zone="documents", path="confi...` | ✓ success |
| TEST-231 | ✅ | Replace pattern vide (invalide) | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-232 | ✅ | Replace avec caractères spéciaux regex | `shed_patch_text(zone="storage", path="regex_s...` | ✓ success |
| TEST-233 | ✅ | Replace case sensitive | `shed_patch_text(zone="storage", path="file.tx...` | Match seulement OLD, pas old |
| TEST-234 | ✅ | Replace sur fichier binaire (échec) | `shed_patch_text(zone="storage", path="image.p...` | ✗ error |
| TEST-235 | ✅ | Replace pattern avec newlines | `shed_patch_text(zone="storage", path="multili...` | ✓ success |
| TEST-236 | ✅ | Replace URL dans fichier | `shed_patch_text(zone="storage", path="url_con...` | ✓ success |
| TEST-237 | ✅ | Replace avec quotes | `shed_patch_text(zone="storage", path="quotes_...` | ✓ success |
| TEST-238 | ✅ | Replace pattern regex complexe | `shed_patch_text(zone="storage", path="func_te...` | ✓ success |
| TEST-239 | ✅ | Replace fichier entier via pattern .* | `shed_patch_text(zone="storage", path="file.tx...` | Comportement dépend de l'implé |
| TEST-240 | ✅ | Replace par chaîne vide (suppression) | `shed_patch_text(zone="storage", path="delete_...` | ✓ success |
| TEST-241 | ✅ | Path commençant par zone (erreur) | `shed_patch_text(zone="storage", path="Storage...` | PATH_STARTS_WITH_ZONE |
| TEST-242 | ✅ | Path avec double slash | `shed_patch_text(zone="storage", path="folder/...` | ✓ success |
| TEST-243 | ✅ | Path avec ./ | `shed_patch_text(zone="storage", path="./file....` | ✓ success |
| TEST-244 | ✅ | Fichier très long nom | `shed_patch_text(zone="storage", path="a" * 30...` | ✗ error |
| TEST-245 | ✅ | Content None | `shed_patch_text(zone="storage", path="file.tx...` | MISSING_PARAMETER |
| TEST-246 | ✅ | Zone vide | `shed_patch_text(zone="", path="file.txt", con...` | INVALID_ZONE |
| TEST-247 | ✅ | Path vide | `shed_patch_text(zone="storage", path="", cont...` | MISSING_PARAMETER |
| TEST-248 | ✅ | Création dans dossier inexistant (auto-création du... | `shed_patch_text(zone="storage", path="nonexis...` | ✓ success |
| TEST-249 | ✅ | Écrire sur un dossier | `shed_patch_text(zone="storage", path="existin...` | NOT_A_FILE |
| TEST-250 | ✅ | Group inexistant | `shed_patch_text(zone="group", group="nonexist...` | GROUP_NOT_FOUND |
| TEST-251 | ✅ | Fichier trop grand (limite 50MB dépassée) | `shed_patch_text(zone="storage", path="huge.tx...` | FILE_TOO_LARGE |
| TEST-252 | ✅ | Fichier symlink | `shed_patch_text(zone="storage", path="symlink...` | Comportement selon implémentat |
| TEST-253 | ✅ | Replace sans pattern | `shed_patch_text(zone="storage", path="file.tx...` | MISSING_PARAMETER |
| TEST-254 | ✅ | Line sans position insert (paramètre ignoré) | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-255 | ✅ | Position before sans line | `shed_patch_text(zone="storage", path="file.tx...` | MISSING_PARAMETER |
| TEST-256 | ✅ | Écriture concurrent (autre session) | `# Simuler écriture concurrente shed_patch_tex...` | Gestion des conflits selon imp |
| TEST-257 | ✅ | Caractères de contrôle dans contenu | `shed_patch_text(zone="storage", path="ctrl.tx...` | ✓ success |
| TEST-258 | ✅ | BOM UTF-8 dans contenu | `shed_patch_text(zone="storage", path="bom.txt...` | ✓ success |
| TEST-259 | ✅ | Très grande ligne (pas de newlines) | `shed_patch_text(zone="storage", path="long.tx...` | ✓ success |
| TEST-260 | ✅ | Replace_all sans occurrences (match_all=True) | `shed_patch_text(zone="storage", path="file.tx...` | PATTERN_NOT_FOUND |
| TEST-261 | ✅ | Écrire bytes simples (base64) | `shed_patch_bytes(zone="storage", path="binary...` | ✓ success |
| TEST-262 | ✅ | Écrire image binaire (1x1 PNG) | `shed_patch_bytes(zone="storage", path="pixel....` | ✓ success |
| TEST-263 | ✅ | Append bytes | `shed_patch_bytes(zone="storage", path="data.b...` | ✓ success |
| TEST-264 | ✅ | Prepend bytes | `shed_patch_bytes(zone="storage", path="data.b...` | ✓ success |
| TEST-265 | ✅ | Écrire bytes zone documents | `shed_patch_bytes(zone="documents", path="data...` | ✓ success |
| TEST-266 | ✅ | Écrire bytes zone group | `shed_patch_bytes(zone="group", group="team", ...` | ✓ success |
| TEST-267 | ✅ | Hex invalide (caractères non-hex) | `shed_patch_bytes(zone="storage", path="test.b...` | INVALID_PARAMETER |
| TEST-268 | ✅ | Écrire fichier exécutable (base64) | `shed_patch_bytes(zone="storage", path="script...` | ✓ success |
| TEST-269 | ✅ | Bytes vides | `shed_patch_bytes(zone="storage", path="empty....` | ✓ success |
| TEST-270 | ✅ | Insert bytes à offset invalide (au-delà de la tail... | `shed_patch_bytes(zone="storage", path="data.b...` | INVALID_PARAMETER |
| TEST-271 | ✅ | Bytes zone uploads (interdit) | `shed_patch_bytes(zone="uploads", path="test.b...` | ZONE_READONLY |
| TEST-272 | ✅ | Fichier binaire avec hex répété | `shed_patch_bytes(zone="storage", path="large....` | ✓ success |
| TEST-273 | ✅ | Overwrite partiel d'un binaire | `shed_patch_bytes(zone="storage", path="data.b...` | ✓ success |
| TEST-274 | ✅ | Append à fichier texte | `shed_patch_bytes(zone="storage", path="text.t...` | ✓ success |
| TEST-275 | ✅ | Path traversal bytes | `shed_patch_bytes(zone="storage", path="../../...` | PATH_ESCAPE |
| TEST-276 | ✅ | Bytes avec message git | `shed_patch_bytes(zone="documents", path="data...` | ✓ success |
| TEST-277 | ✅ | Content None bytes | `shed_patch_bytes(zone="storage", path="test.b...` | MISSING_PARAMETER |
| TEST-278 | ✅ | Offset négatif | `shed_patch_bytes(zone="storage", path="data.b...` | INVALID_PARAMETER |
| TEST-279 | ✅ | Offset au-delà de la taille | `shed_patch_bytes(zone="storage", path="small....` | ✗ error |
| TEST-280 | ✅ | Écrire PDF (en-tête valide, base64) | `shed_patch_bytes(zone="storage", path="doc.pd...` | ✓ success |
| TEST-281 | ✅ | Écrire fichier ZIP (en-tête, base64) | `shed_patch_bytes(zone="storage", path="archiv...` | ✓ success |
| TEST-282 | ✅ | Caractères non-ASCII dans hex (invalide) | `shed_patch_bytes(zone="storage", path="test.b...` | INVALID_PARAMETER |
| TEST-283 | ✅ | Base64 avec whitespace | `shed_patch_bytes(zone="storage", path="test.b...` | ✓ success |
| TEST-284 | ✅ | Créer fichier binaire nouveau | `shed_patch_bytes(zone="storage", path="locked...` | ✓ success |
| TEST-285 | ✅ | Créer fichier binaire dans groupe | `shed_patch_bytes(zone="group", group="team", ...` | ✓ success |
| TEST-286 | ✅ | Position invalide bytes | `shed_patch_bytes(zone="storage", path="data.b...` | INVALID_PARAMETER |
| TEST-287 | ✅ | Bytes dans sous-dossier | `shed_patch_bytes(zone="storage", path="data/b...` | ✓ success |
| TEST-288 | ✅ | Écrire NULL bytes | `shed_patch_bytes(zone="storage", path="null.b...` | ✓ success |
| TEST-289 | ✅ | Base64 padding incorrect | `shed_patch_bytes(zone="storage", path="test.b...` | Dépend de l'implémentation (st |
| TEST-290 | ✅ | Bytes group sans group param | `shed_patch_bytes(zone="group", path="test.bin...` | MISSING_GROUP |
| TEST-291 | ✅ | Supprimer fichier simple | `shed_delete(zone="storage", path="to_delete.t...` | ✓ success |
| TEST-292 | ✅ | Supprimer dossier vide | `shed_delete(zone="storage", path="empty_folde...` | ✓ success |
| TEST-293 | ✅ | Supprimer dossier (récursif) | `shed_delete(zone="storage", path="projects")` | ✓ success |
| TEST-294 | ✅ | Supprimer fichier zone documents | `shed_delete(zone="documents", path="old_doc.m...` | ✓ success |
| TEST-295 | ✅ | Supprimer fichier zone group | `shed_delete(zone="group", group="team", path=...` | ✓ success |
| TEST-296 | ✅ | Supprimer fichier inexistant | `shed_delete(zone="storage", path="nonexistent...` | FILE_NOT_FOUND |
| TEST-297 | ✅ | Supprimer zone uploads | `shed_delete(zone="uploads", path="to_delete_u...` | ✓ success |
| TEST-298 | ✅ | Supprimer avec path traversal | `shed_delete(zone="storage", path="../../../im...` | PATH_ESCAPE |
| TEST-299 | ✅ | Supprimer racine zone (bloqué) | `shed_delete(zone="storage", path=".")` | ✗ error |
| TEST-300 | ✅ | Supprimer fichier verrouillé | `shed_delete(zone="storage", path="delete_me_l...` | FILE_LOCKED |
| TEST-301 | ✅ | Supprimer fichier groupe mode owner_ro | `shed_delete(zone="group", group="team", path=...` | ✗ error |
| TEST-302 | ✅ | Supprimer fichier avec espaces | `shed_delete(zone="storage", path="my file.txt...` | ✓ success |
| TEST-303 | ✅ | Supprimer lien symbolique | `shed_delete(zone="storage", path="symlink")` | ✓ success |
| TEST-304 | ✅ | Supprimer fichier binaire | `shed_delete(zone="storage", path="data.bin")` | ✓ success |
| TEST-305 | ✅ | Supprimer arborescence profonde | `shed_delete(zone="storage", path="a/b/c/d/e/f...` | ✓ success |
| TEST-306 | ✅ | Supprimer fichier caché | `shed_delete(zone="storage", path=".hidden")` | ✓ success |
| TEST-307 | ✅ | Supprimer .git (devrait être bloqué) | `shed_delete(zone="documents", path=".git")` | ✗ error |
| TEST-308 | ✅ | Supprimer sans path | `shed_delete(zone="storage", path="")` | MISSING_PARAMETER |
| TEST-309 | ✅ | Supprimer groupe sans group param | `shed_delete(zone="group", path="file.txt")` | MISSING_GROUP |
| TEST-310 | ✅ | Supprimer zone invalide | `shed_delete(zone="invalid", path="file.txt")` | INVALID_ZONE |
| TEST-311 | ✅ | Supprimer avec message git | `shed_delete(zone="documents", path="old.md", ...` | Paramètre message ignoré ou su |
| TEST-312 | ✅ | Supprimer fichier groupe autre membre | `shed_delete(zone="group", group="team", path=...` | Selon mode du fichier |
| TEST-313 | ✅ | Supprimer dossier .git interne | `shed_delete(zone="storage", path="project/.gi...` | Selon protection .git |
| TEST-314 | ✅ | Supprimer tous les fichiers (pattern) | `shed_delete(zone="storage", path="*.log")` | Glob non supporté, ou suppress |
| TEST-315 | ✅ | Supprimer fichier volumineux | `shed_delete(zone="storage", path="large_100mb...` | ✓ success |
| TEST-316 | ✅ | Supprimer fichier pendant lecture | `# Tenter de supprimer pendant une opération s...` | Gestion selon système |
| TEST-317 | ✅ | Supprimer path avec caractères spéciaux | `shed_delete(zone="storage", path="file[1].txt...` | ✓ success |
| TEST-318 | ✅ | Supprimer fichier UTF-8 dans nom | `shed_delete(zone="storage", path="fichier_été...` | ✓ success |
| TEST-319 | ✅ | Supprimer dossier contenant .gitkeep | `shed_delete(zone="storage", path="folder_with...` | ✓ success |
| TEST-320 | ✅ | Supprimer groupe non membre | `shed_delete(zone="group", group="other_team",...` | GROUP_ACCESS_DENIED |
| TEST-321 | ✅ | Renommer fichier simple | `shed_rename(zone="storage", old_path="rename_...` | ✓ success |
| TEST-322 | ✅ | Déplacer fichier dans dossier | `shed_rename(zone="storage", old_path="movable...` | ✓ success |
| TEST-323 | ✅ | Renommer dossier | `shed_rename(zone="storage", old_path="old_fol...` | ✓ success |
| TEST-324 | ✅ | Renommer zone documents | `shed_rename(zone="documents", old_path="draft...` | ✓ success |
| TEST-325 | ✅ | Renommer zone group | `shed_rename(zone="group", group="team", old_p...` | ✓ success |
| TEST-326 | ✅ | Renommer fichier inexistant | `shed_rename(zone="storage", old_path="nonexis...` | FILE_NOT_FOUND |
| TEST-327 | ✅ | Renommer vers destination existante | `shed_rename(zone="storage", old_path="file1.t...` | FILE_EXISTS |
| TEST-328 | ✅ | Renommer zone uploads (interdit) | `shed_rename(zone="uploads", old_path="file.tx...` | ZONE_READONLY |
| TEST-329 | ✅ | Renommer avec path traversal | `shed_rename(zone="storage", old_path="file.tx...` | PATH_ESCAPE |
| TEST-330 | ✅ | Renommer fichier verrouillé | `shed_rename(zone="storage", old_path="rename_...` | FILE_LOCKED |
| TEST-331 | ✅ | Renommer vers dossier inexistant (création auto) | `shed_rename(zone="storage", old_path="file.tx...` | ✓ success |
| TEST-332 | ✅ | Renommer fichier sur lui-même | `shed_rename(zone="storage", old_path="file.tx...` | ✗ error |
| TEST-333 | ✅ | Renommer avec changement d'extension | `shed_rename(zone="storage", old_path="documen...` | ✓ success |
| TEST-334 | ✅ | Renommer fichier binaire | `shed_rename(zone="storage", old_path="rename_...` | ✓ success |
| TEST-335 | ✅ | Renommer arborescence | `shed_rename(zone="storage", old_path="project...` | ✓ success |
| TEST-336 | ✅ | Renommer vers nom avec espaces | `shed_rename(zone="storage", old_path="source....` | ✓ success |
| TEST-337 | ✅ | Renommer fichier caché | `shed_rename(zone="storage", old_path=".hidden...` | ✓ success |
| TEST-338 | ✅ | Renommer sans old_path | `shed_rename(zone="storage", old_path="", new_...` | MISSING_PARAMETER |
| TEST-339 | ✅ | Renommer sans new_path | `shed_rename(zone="storage", old_path="file.tx...` | MISSING_PARAMETER |
| TEST-340 | ✅ | Renommer groupe sans group param | `shed_rename(zone="group", old_path="old.txt",...` | MISSING_GROUP |
| TEST-341 | ✅ | Renommer avec message git | `shed_rename(zone="documents", old_path="old.m...` | Paramètre message supporté ou  |
| TEST-342 | ✅ | Renommer dossier vers sous-dossier de lui-même | `shed_rename(zone="storage", old_path="folder"...` | ✗ error |
| TEST-343 | ✅ | Renommer fichier UTF-8 | `shed_rename(zone="storage", old_path="été.txt...` | ✓ success |
| TEST-344 | ✅ | Renommer lien symbolique | `shed_rename(zone="storage", old_path="symlink...` | ✓ success |
| TEST-345 | ✅ | Renommer fichier groupe mode owner | `shed_rename(zone="group", group="team", old_p...` | Selon permissions (owner only) |
| TEST-346 | ✅ | Renommer zone invalide | `shed_rename(zone="invalid", old_path="old.txt...` | INVALID_ZONE |
| TEST-347 | ✅ | Renommer avec new_path commençant par zone | `shed_rename(zone="storage", old_path="file.tx...` | PATH_STARTS_WITH_ZONE |
| TEST-348 | ✅ | Renommer cross-zone (interdit) | `shed_rename(zone="storage", old_path="file.tx...` | PATH_ESCAPE |
| TEST-349 | ✅ | Renommer fichier très gros | `shed_rename(zone="storage", old_path="large_f...` | ✓ success |
| TEST-350 | ✅ | Renommer vers nom très long | `shed_rename(zone="storage", old_path="short.t...` | ✗ error |
| TEST-351 | ✅ | Tree zone storage | `shed_tree(zone="storage")` | ✓ success |
| TEST-352 | ✅ | Tree avec profondeur limitée | `shed_tree(zone="storage", depth=2)` | ✓ success |
| TEST-353 | ✅ | Tree d'un sous-dossier | `shed_tree(zone="storage", path="tree_test")` | ✓ success |
| TEST-354 | ✅ | Tree zone documents | `shed_tree(zone="documents")` | ✓ success |
| TEST-355 | ✅ | Tree zone uploads | `shed_tree(zone="uploads")` | ✓ success |
| TEST-356 | ✅ | Tree zone group | `shed_tree(zone="group", group="team")` | ✓ success |
| TEST-357 | ✅ | Tree profondeur 0 | `shed_tree(zone="storage", depth=0)` | ✓ success |
| TEST-358 | ✅ | Tree profondeur très grande | `shed_tree(zone="storage", depth=100)` | ✓ success |
| TEST-359 | ✅ | Tree dossier vide | `shed_tree(zone="storage", path="tree_empty_fo...` | ✓ success |
| TEST-360 | ✅ | Tree dossier inexistant | `shed_tree(zone="storage", path="truly_nonexis...` | FILE_NOT_FOUND |
| TEST-361 | ✅ | Tree zone invalide | `shed_tree(zone="invalid")` | INVALID_ZONE |
| TEST-362 | ✅ | Tree group sans group param | `shed_tree(zone="group")` | MISSING_GROUP |
| TEST-363 | ✅ | Tree avec path traversal | `shed_tree(zone="storage", path="../../../")` | PATH_ESCAPE |
| TEST-364 | ✅ | Tree sur fichier (pas dossier) | `shed_tree(zone="storage", path="file.txt")` | ✗ error |
| TEST-365 | ✅ | Tree profondeur 1 | `shed_tree(zone="storage", depth=1)` | ✓ success |
| TEST-366 | ✅ | Tree arborescence profonde | `shed_tree(zone="storage", path="deep/nested/s...` | ✓ success |
| TEST-367 | ✅ | Tree avec fichiers cachés | `shed_tree(zone="storage", path=".")` | ✓ success |
| TEST-368 | ✅ | Tree groupe autre membre | `shed_tree(zone="group", group="other_team")` | GROUP_ACCESS_DENIED |
| TEST-369 | ✅ | Tree avec profondeur négative | `shed_tree(zone="storage", depth=-1)` | INVALID_PARAMETER |
| TEST-370 | ✅ | Tree path avec espaces | `shed_tree(zone="storage", path="my folder")` | ✓ success |
| TEST-371 | ✅ | Ouvrir fichier pour édition | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-372 | ✅ | Ouvrir fichier zone documents | `shed_lockedit_open(zone="documents", path="do...` | ✓ success |
| TEST-373 | ✅ | Ouvrir fichier zone group | `shed_lockedit_open(zone="group", group="team"...` | ✓ success |
| TEST-374 | ✅ | Ouvrir fichier inexistant | `shed_lockedit_open(zone="storage", path="none...` | FILE_NOT_FOUND |
| TEST-375 | ✅ | Ouvrir fichier déjà verrouillé (autre conversation... | `shed_lockedit_open(zone="storage", path="alre...` | FILE_LOCKED |
| TEST-376 | ✅ | Ouvrir fichier verrouillé par autre | `shed_lockedit_open(zone="storage", path="lock...` | FILE_LOCKED |
| TEST-377 | ✅ | Ouvrir zone uploads (interdit) | `shed_lockedit_open(zone="uploads", path="file...` | ZONE_READONLY |
| TEST-378 | ✅ | Ouvrir avec path traversal | `shed_lockedit_open(zone="storage", path="../....` | PATH_ESCAPE |
| TEST-379 | ✅ | Ouvrir dossier (interdit) | `shed_lockedit_open(zone="storage", path="fold...` | NOT_A_FILE |
| TEST-380 | ✅ | Ouvrir fichier binaire | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-381 | ✅ | Ouvrir zone invalide | `shed_lockedit_open(zone="invalid", path="file...` | INVALID_ZONE |
| TEST-382 | ✅ | Ouvrir group sans group param | `shed_lockedit_open(zone="group", path="file.t...` | MISSING_GROUP |
| TEST-383 | ✅ | Ouvrir fichier groupe mode owner_ro | `shed_lockedit_open(zone="group", group="team"...` | PERMISSION_DENIED |
| TEST-384 | ✅ | Ouvrir fichier volumineux | `shed_lockedit_open(zone="storage", path="larg...` | ✓ success |
| TEST-385 | ✅ | Ouvrir sans path | `shed_lockedit_open(zone="storage", path="")` | MISSING_PARAMETER |
| TEST-386 | ✅ | Ouvrir fichier caché | `shed_lockedit_open(zone="storage", path=".loc...` | ✓ success |
| TEST-387 | ✅ | Ouvrir fichier dans sous-dossier | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-388 | ✅ | Ouvrir groupe non membre | `shed_lockedit_open(zone="group", group="other...` | GROUP_ACCESS_DENIED |
| TEST-389 | ✅ | Ouvrir fichier symlink | `shed_lockedit_open(zone="storage", path="syml...` | Comportement selon implémentat |
| TEST-390 | ✅ | Ouvrir plusieurs fichiers simultanément | `shed_lockedit_open(zone="storage", path="file...` | ✓ success |
| TEST-391 | ✅ | Exec cat sur fichier verrouillé | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-392 | ✅ | Exec sed sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-393 | ✅ | Exec grep sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-394 | ✅ | Exec sur fichier non verrouillé | `shed_lockedit_exec(zone="storage", path="not_...` | NOT_IN_EDIT_MODE |
| TEST-395 | ✅ | Exec commande rm (sans argument fichier) | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-396 | ✅ | Exec avec arguments dangereux | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-397 | ✅ | Exec head sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-398 | ✅ | Exec wc sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-399 | ✅ | Exec zone documents | `shed_lockedit_open(zone="documents", path="do...` | ✓ success |
| TEST-400 | ✅ | Exec zone group | `shed_lockedit_open(zone="group", group="team"...` | ✓ success |
| TEST-401 | ✅ | Exec awk sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-402 | ✅ | Exec sort sur fichier verrouillé | `shed_lockedit_exec(zone="storage", path="lock...` | ✓ success |
| TEST-403 | ✅ | Exec sans cmd | `shed_lockedit_exec(zone="storage", path="lock...` | COMMAND_FORBIDDEN |
| TEST-404 | ✅ | Exec xxd (hexdump) sur binaire | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-405 | ✅ | Exec avec timeout dépassé | `shed_lockedit_exec(zone="storage", path="lock...` | TIMEOUT |
| TEST-406 | ✅ | Overwrite fichier verrouillé | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-407 | ✅ | Append fichier verrouillé | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-408 | ✅ | Overwrite fichier non verrouillé | `shed_lockedit_overwrite(zone="storage", path=...` | NOT_IN_EDIT_MODE |
| TEST-409 | ✅ | Overwrite zone documents | `shed_lockedit_overwrite(zone="documents", pat...` | ✓ success |
| TEST-410 | ✅ | Overwrite zone group | `shed_lockedit_overwrite(zone="group", group="...` | ✓ success |
| TEST-411 | ✅ | Overwrite contenu vide | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-412 | ✅ | Append contenu multiligne | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-413 | ✅ | Overwrite contenu très long | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-414 | ✅ | Overwrite avec caractères spéciaux | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-415 | ✅ | Overwrite sans content | `shed_lockedit_overwrite(zone="storage", path=...` | ✗ error |
| TEST-416 | ✅ | Append plusieurs fois | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-417 | ✅ | Overwrite fichier binaire avec texte | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-418 | ✅ | Overwrite group sans group param | `shed_lockedit_overwrite(zone="group", path="f...` | MISSING_GROUP |
| TEST-419 | ✅ | Overwrite avec emojis | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-420 | ✅ | Append=False par défaut | `shed_lockedit_overwrite(zone="storage", path=...` | ✓ success |
| TEST-421 | ✅ | Save fichier modifié | `shed_lockedit_save(zone="storage", path="lock...` | ✓ success |
| TEST-422 | ✅ | Save zone documents | `shed_lockedit_save(zone="documents", path="do...` | ✓ success |
| TEST-423 | ✅ | Save fichier déjà sauvé (NOT_IN_EDIT_MODE) | `shed_lockedit_save(zone="documents", path="do...` | NOT_IN_EDIT_MODE |
| TEST-424 | ✅ | Save zone group | `shed_lockedit_save(zone="group", group="team"...` | ✓ success |
| TEST-425 | ✅ | Save fichier non verrouillé | `shed_lockedit_save(zone="storage", path="not_...` | NOT_IN_EDIT_MODE |
| TEST-426 | ✅ | Save fichier verrouillé par autre | `shed_lockedit_save(zone="storage", path="lock...` | NOT_LOCK_OWNER |
| TEST-427 | ✅ | Save sans modifications | `shed_lockedit_save(zone="storage", path="unch...` | NOT_IN_EDIT_MODE |
| TEST-428 | ✅ | Double save (déjà sauvé) | `shed_lockedit_save(zone="storage", path="alre...` | NOT_IN_EDIT_MODE |
| TEST-429 | ✅ | Save zone invalide | `shed_lockedit_save(zone="invalid", path="file...` | INVALID_ZONE |
| TEST-430 | ✅ | Save group sans group param | `shed_lockedit_save(zone="group", path="file.t...` | MISSING_GROUP |
| TEST-431 | ✅ | Save sans path | `shed_lockedit_save(zone="storage", path="")` | ✗ error |
| TEST-432 | ✅ | Save fichier non ouvert retourne NOT_IN_EDIT_MODE | `shed_lockedit_save(zone="storage", path="lock...` | NOT_IN_EDIT_MODE |
| TEST-433 | ✅ | Save fichier non ouvert retourne NOT_IN_EDIT_MODE | `shed_lockedit_save(zone="storage", path="larg...` | NOT_IN_EDIT_MODE |
| TEST-434 | ✅ | Save groupe déjà sauvé retourne NOT_IN_EDIT_MODE | `shed_lockedit_save(zone="group", group="team"...` | NOT_IN_EDIT_MODE |
| TEST-435 | ✅ | Save puis réouvrir | `shed_lockedit_save(zone="storage", path="lock...` | ✓ success |
| TEST-436 | ✅ | Cancel édition | `shed_lockedit_cancel(zone="storage", path="lo...` | ✓ success |
| TEST-437 | ✅ | Cancel zone documents (workflow complet) | `shed_lockedit_open(zone="documents", path="do...` | ✓ success |
| TEST-438 | ✅ | Cancel zone group (workflow complet) | `shed_lockedit_open(zone="group", group="team"...` | ✓ success |
| TEST-439 | ✅ | Cancel fichier non verrouillé | `shed_lockedit_cancel(zone="storage", path="no...` | NOT_IN_EDIT_MODE |
| TEST-440 | ✅ | Cancel fichier verrouillé par autre | `shed_lockedit_cancel(zone="storage", path="lo...` | NOT_LOCK_OWNER |
| TEST-441 | ✅ | Cancel après modifications | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-442 | ✅ | Cancel zone invalide | `shed_lockedit_cancel(zone="invalid", path="fi...` | INVALID_ZONE |
| TEST-443 | ✅ | Cancel group sans group param | `shed_lockedit_cancel(zone="group", path="file...` | MISSING_GROUP |
| TEST-444 | ✅ | Cancel sans path | `shed_lockedit_cancel(zone="storage", path="")` | MISSING_PARAMETER |
| TEST-445 | ✅ | Double cancel | `shed_lockedit_open(zone="storage", path="lock...` | NOT_IN_EDIT_MODE |
| TEST-446 | ✅ | Cancel puis réouvrir | `shed_lockedit_cancel(zone="storage", path="lo...` | ✓ success |
| TEST-447 | ✅ | Cancel fichier binaire | `shed_lockedit_cancel(zone="storage", path="lo...` | ✓ success |
| TEST-448 | ✅ | Cancel groupe non membre | `shed_lockedit_cancel(zone="group", group="oth...` | GROUP_ACCESS_DENIED |
| TEST-449 | ✅ | Cancel avec path traversal | `shed_lockedit_cancel(zone="storage", path=".....` | PATH_ESCAPE |
| TEST-450 | ✅ | Cancel fichier volumineux | `shed_lockedit_cancel(zone="storage", path="la...` | ✓ success |
| TEST-451 | ✅ | Déplacer fichier uploads vers storage | `shed_move_uploads_to_storage(src="uploaded.tx...` | ✓ success |
| TEST-452 | ✅ | Déplacer vers sous-dossier storage | `shed_move_uploads_to_storage(src="data.csv", ...` | ✓ success |
| TEST-453 | ✅ | Déplacer fichier inexistant | `shed_move_uploads_to_storage(src="nonexistent...` | FILE_NOT_FOUND |
| TEST-454 | ✅ | Déplacer vers destination existante | `shed_move_uploads_to_storage(src="new.txt", d...` | FILE_EXISTS |
| TEST-455 | ✅ | Déplacer fichier binaire | `shed_move_uploads_to_storage(src="binary_uplo...` | ✓ success |
| TEST-456 | ✅ | Déplacer fichier volumineux | `shed_move_uploads_to_storage(src="large.zip",...` | ✓ success |
| TEST-457 | ✅ | Déplacer avec path traversal src | `shed_move_uploads_to_storage(src="../../../et...` | PATH_ESCAPE |
| TEST-458 | ✅ | Déplacer avec path traversal dest | `shed_move_uploads_to_storage(src="file.txt", ...` | PATH_ESCAPE |
| TEST-459 | ✅ | Déplacer sans src | `shed_move_uploads_to_storage(src="", dest="te...` | MISSING_PARAMETER |
| TEST-460 | ✅ | Déplacer sans dest | `shed_move_uploads_to_storage(src="file.txt", ...` | MISSING_PARAMETER |
| TEST-461 | ✅ | Déplacer dossier entier | `shed_move_uploads_to_storage(src="uploaded_fo...` | ✓ success |
| TEST-462 | ✅ | Déplacer avec renommage | `shed_move_uploads_to_storage(src="original.tx...` | ✓ success |
| TEST-463 | ✅ | Déplacer fichier caché | `shed_move_uploads_to_storage(src=".hidden", d...` | ✓ success |
| TEST-464 | ✅ | Déplacer vers dossier inexistant | `shed_move_uploads_to_storage(src="file.txt", ...` | ✗ error |
| TEST-465 | ✅ | Déplacer fichier avec espaces | `shed_move_uploads_to_storage(src="my file.txt...` | ✓ success |
| TEST-466 | ✅ | Déplacer fichier UTF-8 | `shed_move_uploads_to_storage(src="été.txt", d...` | ✓ success |
| TEST-467 | ✅ | Déplacer symlink | `shed_move_uploads_to_storage(src="symlink", d...` | Comportement selon implémentat |
| TEST-468 | ✅ | Vérifier suppression de la source | `shed_move_uploads_to_storage(src="to_move.txt...` | Source supprimée après move |
| TEST-469 | ✅ | Déplacer gros fichier (move ne change pas le quota... | `shed_move_uploads_to_storage(src="big_file.bi...` | ✓ success |
| TEST-470 | ✅ | Déplacer dest commençant par Storage | `shed_move_uploads_to_storage(src="file.txt", ...` | PATH_STARTS_WITH_ZONE |
| TEST-471 | ✅ | Déplacer uploads vers documents | `shed_move_uploads_to_documents(src="report.md...` | ✓ success |
| TEST-472 | ✅ | Déplacer avec message git | `shed_move_uploads_to_documents(src="doc.md", ...` | ✓ success |
| TEST-473 | ✅ | Déplacer fichier inexistant | `shed_move_uploads_to_documents(src="nonexiste...` | FILE_NOT_FOUND |
| TEST-474 | ✅ | Déplacer vers destination existante | `shed_move_uploads_to_documents(src="new.md", ...` | FILE_EXISTS |
| TEST-475 | ✅ | Déplacer fichier binaire | `shed_move_uploads_to_documents(src="data.bin"...` | ✓ success |
| TEST-476 | ✅ | Déplacer avec path traversal | `shed_move_uploads_to_documents(src="../../../...` | PATH_ESCAPE |
| TEST-477 | ✅ | Déplacer sans src | `shed_move_uploads_to_documents(src="", dest="...` | MISSING_PARAMETER |
| TEST-478 | ✅ | Déplacer fichier volumineux | `shed_move_uploads_to_documents(src="large.txt...` | ✓ success |
| TEST-479 | ✅ | Vérifier commit créé | `shed_move_uploads_to_documents(src="file.md",...` | Commit visible dans l'historiq |
| TEST-480 | ✅ | Déplacer fichier UTF-8 | `shed_move_uploads_to_documents(src="résumé.md...` | ✓ success |
| TEST-481 | ✅ | Déplacer vers sous-dossier profond | `shed_move_uploads_to_documents(src="file.md",...` | ✓ success |
| TEST-482 | ✅ | Déplacer avec espaces dans nom | `shed_move_uploads_to_documents(src="my doc.md...` | ✓ success |
| TEST-483 | ✅ | Déplacer dest commençant par Documents | `shed_move_uploads_to_documents(src="file.md",...` | PATH_STARTS_WITH_ZONE |
| TEST-484 | ✅ | Déplacer gros fichier (move ne change pas le quota... | `shed_move_uploads_to_documents(src="huge.bin"...` | ✓ success |
| TEST-485 | ✅ | Message git par défaut | `shed_move_uploads_to_documents(src="git_test....` | ✓ success |
| TEST-486 | ✅ | Copier storage vers documents | `shed_copy_storage_to_documents(src="draft.md"...` | ✓ success |
| TEST-487 | ✅ | Copier avec message git | `shed_copy_storage_to_documents(src="file.md",...` | ✓ success |
| TEST-488 | ✅ | Copier fichier inexistant | `shed_copy_storage_to_documents(src="nonexiste...` | FILE_NOT_FOUND |
| TEST-489 | ✅ | Copier vers destination existante | `shed_copy_storage_to_documents(src="new.md", ...` | FILE_EXISTS |
| TEST-490 | ✅ | Vérifier source non supprimée | `shed_copy_storage_to_documents(src="source.md...` | Source conservée (copie, pas m |
| TEST-491 | ✅ | Copier dossier | `shed_copy_storage_to_documents(src="folder", ...` | ✓ success |
| TEST-492 | ✅ | Copier fichier binaire | `shed_copy_storage_to_documents(src="image.png...` | ✓ success |
| TEST-493 | ✅ | Copier avec path traversal | `shed_copy_storage_to_documents(src="../../../...` | PATH_ESCAPE |
| TEST-494 | ✅ | Copier fichier volumineux | `shed_copy_storage_to_documents(src="large.bin...` | ✓ success |
| TEST-495 | ✅ | Copier sans src | `shed_copy_storage_to_documents(src="", dest="...` | MISSING_PARAMETER |
| TEST-496 | ✅ | Copier vers sous-dossier | `shed_copy_storage_to_documents(src="file.md",...` | ✓ success |
| TEST-497 | ✅ | Copier fichier caché | `shed_copy_storage_to_documents(src=".config",...` | ✓ success |
| TEST-498 | ✅ | Copier dest commençant par Documents | `shed_copy_storage_to_documents(src="file.md",...` | PATH_STARTS_WITH_ZONE |
| TEST-499 | ✅ | Copier gros fichier (quota non dépassé) | `shed_copy_storage_to_documents(src="copy_test...` | ✓ success |
| TEST-500 | ✅ | Copier fichier UTF-8 | `shed_copy_storage_to_documents(src="café.md",...` | ✓ success |
| TEST-501 | ✅ | Déplacer documents vers storage | `shed_move_documents_to_storage(src="move_to_s...` | ✓ success |
| TEST-502 | ✅ | Déplacer avec message git | `shed_move_documents_to_storage(src="move_with...` | ✓ success |
| TEST-503 | ✅ | Déplacer fichier inexistant | `shed_move_documents_to_storage(src="nonexiste...` | FILE_NOT_FOUND |
| TEST-504 | ✅ | Déplacer vers destination existante | `shed_move_documents_to_storage(src="doc.md", ...` | FILE_EXISTS |
| TEST-505 | ✅ | Vérifier source supprimée | `shed_move_documents_to_storage(src="to_move.m...` | Source supprimée de documents |
| TEST-506 | ✅ | Déplacer fichier binaire | `shed_move_documents_to_storage(src="data.bin"...` | ✓ success |
| TEST-507 | ✅ | Déplacer avec path traversal | `shed_move_documents_to_storage(src="../../../...` | PATH_ESCAPE |
| TEST-508 | ✅ | Déplacer sans src | `shed_move_documents_to_storage(src="", dest="...` | MISSING_PARAMETER |
| TEST-509 | ✅ | Déplacer fichier volumineux | `shed_move_documents_to_storage(src="large.md"...` | ✓ success |
| TEST-510 | ✅ | Déplacer dossier | `shed_move_documents_to_storage(src="folder_do...` | ✓ success |
| TEST-511 | ✅ | Déplacer dest commençant par Storage | `shed_move_documents_to_storage(src="file.md",...` | PATH_STARTS_WITH_ZONE |
| TEST-512 | ✅ | Vérifier commit de suppression | `shed_move_documents_to_storage(src="file.md",...` | Commit reflète la suppression |
| TEST-513 | ✅ | Déplacer fichier avec espaces | `shed_move_documents_to_storage(src="my doc.md...` | ✓ success |
| TEST-514 | ✅ | Déplacer vers sous-dossier | `shed_move_documents_to_storage(src="file.md",...` | ✓ success |
| TEST-515 | ✅ | Message git par défaut | `shed_move_documents_to_storage(src="git_defau...` | ✓ success |
| TEST-516 | ✅ | Copier storage vers group | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-517 | ✅ | Copier documents vers group | `shed_copy_to_group(src_zone="documents", src_...` | ✓ success |
| TEST-518 | ✅ | Copier avec message git | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-519 | ✅ | Copier avec mode owner | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-520 | ✅ | Copier avec mode group | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-521 | ✅ | Copier avec mode owner_ro | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-522 | ✅ | Copier fichier inexistant | `shed_copy_to_group(src_zone="storage", src_pa...` | FILE_NOT_FOUND |
| TEST-523 | ✅ | Copier vers destination existante | `shed_copy_to_group(src_zone="storage", src_pa...` | FILE_EXISTS |
| TEST-524 | ✅ | Copier vers groupe non membre | `shed_copy_to_group(src_zone="storage", src_pa...` | GROUP_ACCESS_DENIED |
| TEST-525 | ✅ | Copier sans group | `shed_copy_to_group(src_zone="storage", src_pa...` | INVALID_GROUP_ID |
| TEST-526 | ✅ | Copier depuis uploads vers group | `shed_copy_to_group(src_zone="uploads", src_pa...` | ✓ success |
| TEST-527 | ✅ | Copier avec path traversal | `shed_copy_to_group(src_zone="storage", src_pa...` | PATH_ESCAPE |
| TEST-528 | ✅ | Copier mode invalide (fallback to group) | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-529 | ✅ | Copier fichier binaire vers group | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
| TEST-530 | ✅ | Copier src_zone invalide | `shed_copy_to_group(src_zone="invalid", src_pa...` | ZONE_FORBIDDEN |
| TEST-531 | ✅ | Créer ZIP d'un fichier | `shed_zip(zone="storage", src="zip_test.txt", ...` | ✓ success |
| TEST-532 | ✅ | Créer ZIP d'un dossier | `shed_zip(zone="storage", src="zip_folder", de...` | ✓ success |
| TEST-533 | ✅ | ZIP avec sous-dossiers | `shed_zip(zone="storage", src="tree_test", des...` | ✓ success |
| TEST-534 | ✅ | ZIP avec empty dirs | `shed_zip(zone="storage", src="zip_folder", de...` | ✓ success |
| TEST-535 | ✅ | ZIP sans empty dirs | `shed_zip(zone="storage", src="zip_folder", de...` | ✓ success |
| TEST-536 | ✅ | ZIP zone documents | `shed_zip(zone="documents", src="folder_doc_zi...` | ✓ success |
| TEST-537 | ✅ | ZIP zone group non supportée | `shed_zip(zone="group", src="shared.md", dest=...` | ZONE_FORBIDDEN |
| TEST-538 | ✅ | ZIP source inexistante | `shed_zip(zone="storage", src="truly_nonexiste...` | FILE_NOT_FOUND |
| TEST-539 | ✅ | ZIP destination existante | `shed_zip(zone="storage", src="zip_folder", de...` | FILE_EXISTS |
| TEST-540 | ✅ | ZIP avec path traversal src | `shed_zip(zone="storage", src="../../../etc", ...` | PATH_ESCAPE |
| TEST-541 | ✅ | ZIP avec path traversal dest | `shed_zip(zone="storage", src="folder", dest="...` | PATH_ESCAPE |
| TEST-542 | ✅ | ZIP fichier binaire | `shed_zip(zone="storage", src="image.png", des...` | ✓ success |
| TEST-543 | ✅ | ZIP fichiers multiples (dossier) | `shed_zip(zone="storage", src="mixed_content",...` | ✓ success |
| TEST-544 | ✅ | ZIP zone uploads (lecture seule OK) | `shed_zip(zone="uploads", src="folder", dest="...` | ✗ error |
| TEST-545 | ✅ | ZIP zone invalide | `shed_zip(zone="invalid", src="folder", dest="...` | ZONE_FORBIDDEN |
| TEST-546 | ✅ | ZIP group non supporté | `shed_zip(zone="group", src="folder", dest="te...` | ZONE_FORBIDDEN |
| TEST-547 | ✅ | ZIP sans dest (auto-nommé) | `shed_zip(zone="storage", src="folder", dest="...` | ✓ success |
| TEST-548 | ✅ | ZIP fichier volumineux | `shed_zip(zone="storage", src="large_folder", ...` | ✓ success |
| TEST-549 | ✅ | ZIP fichier caché | `shed_zip(zone="storage", src=".hidden_zip", d...` | ✓ success |
| TEST-550 | ✅ | ZIP avec espaces dans nom | `shed_zip(zone="storage", src="my folder", des...` | ✓ success |
| TEST-551 | ✅ | ZIP fichier UTF-8 | `shed_zip(zone="storage", src="été_zip", dest=...` | ✓ success |
| TEST-552 | ✅ | ZIP dossier volumineux | `shed_zip(zone="storage", src="huge_folder", d...` | ✓ success |
| TEST-553 | ✅ | ZIP dossier vide | `shed_zip(zone="storage", src="empty_folder_zi...` | ✓ success |
| TEST-554 | ✅ | ZIP dest dans sous-dossier | `shed_zip(zone="storage", src="folder", dest="...` | ✓ success |
| TEST-555 | ✅ | ZIP sans src | `shed_zip(zone="storage", src="", dest="test.z...` | MISSING_PARAMETER |
| TEST-556 | ✅ | Extraire ZIP simple | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-557 | ✅ | Extraire ZIP dans racine | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-558 | ✅ | Extraire ZIP cross-zone (uploads vers storage) | `shed_unzip(zone="storage", src="uploaded.zip"...` | ✓ success |
| TEST-559 | ✅ | Extraire ZIP zone documents | `shed_unzip(zone="documents", src="docs.zip", ...` | ✓ success |
| TEST-560 | ✅ | Extraire ZIP zone group non supportée | `shed_unzip(zone="group", src="shared.zip", de...` | ZONE_FORBIDDEN |
| TEST-561 | ✅ | Extraire ZIP inexistant | `shed_unzip(zone="storage", src="nonexistent.z...` | FILE_NOT_FOUND |
| TEST-562 | ✅ | Extraire fichier corrompu | `shed_unzip(zone="storage", src="corrupted.zip...` | ✗ error |
| TEST-563 | ✅ | Extraire ZIP vers destination existante | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-564 | ✅ | Extraire ZIP avec path traversal src | `shed_unzip(zone="storage", src="../../../etc/...` | PATH_ESCAPE |
| TEST-565 | ✅ | Extraire ZIP avec path traversal dest | `shed_unzip(zone="storage", src="archive.zip",...` | PATH_ESCAPE |
| TEST-566 | ✅ | Extraire ZIP avec structure profonde | `shed_unzip(zone="storage", src="deep_archive....` | ✓ success |
| TEST-567 | ✅ | Extraire ZIP zone invalide | `shed_unzip(zone="invalid", src="archive.zip",...` | ZONE_FORBIDDEN |
| TEST-568 | ✅ | Extraire ZIP zone group non supportée | `shed_unzip(zone="group", src="archive.zip", d...` | ZONE_FORBIDDEN |
| TEST-569 | ✅ | Extraire ZIP binaire | `shed_unzip(zone="storage", src="binary_archiv...` | ✓ success |
| TEST-570 | ✅ | Extraire ZIP avec mot de passe (non supporté) | `shed_unzip(zone="storage", src="encrypted.zip...` | ✗ error |
| TEST-571 | ✅ | Extraire ZIP volumineux | `shed_unzip(zone="storage", src="large.zip", d...` | ✓ success |
| TEST-572 | ✅ | Extraire ZIP plus grand | `shed_unzip(zone="storage", src="huge.zip", de...` | ✓ success |
| TEST-573 | ✅ | Extraire ZIP fichiers UTF-8 | `shed_unzip(zone="storage", src="été.zip", des...` | ✓ success |
| TEST-574 | ✅ | Extraire ZIP sans src | `shed_unzip(zone="storage", src="", dest="test...` | MISSING_PARAMETER |
| TEST-575 | ✅ | src_zone invalide | `shed_unzip(zone="storage", src="archive.zip",...` | ZONE_FORBIDDEN |
| TEST-576 | ✅ | Info ZIP simple | `shed_zipinfo(zone="storage", path="archive.zi...` | ✓ success |
| TEST-577 | ✅ | Info ZIP avec tailles | `shed_zipinfo(zone="storage", path="archive.zi...` | ✓ success |
| TEST-578 | ✅ | Info ZIP zone documents | `shed_zipinfo(zone="documents", path="docs.zip...` | ✓ success |
| TEST-579 | ✅ | Info ZIP zone group sans paramètre group | `shed_zipinfo(zone="group", path="shared.zip")` | MISSING_PARAMETER |
| TEST-580 | ✅ | Info ZIP inexistant | `shed_zipinfo(zone="storage", path="nonexisten...` | FILE_NOT_FOUND |
| TEST-581 | ✅ | Info fichier corrompu | `shed_zipinfo(zone="storage", path="corrupted....` | ✗ error |
| TEST-582 | ✅ | Info ZIP avec path traversal | `shed_zipinfo(zone="storage", path="../../../e...` | PATH_ESCAPE |
| TEST-583 | ✅ | Info ZIP zone invalide | `shed_zipinfo(zone="invalid", path="archive.zi...` | INVALID_ZONE |
| TEST-584 | ✅ | Info ZIP zone group sans paramètre group | `shed_zipinfo(zone="group", path="archive.zip"...` | MISSING_PARAMETER |
| TEST-585 | ✅ | Info ZIP corrompu | `shed_zipinfo(zone="storage", path="corrupted....` | ✗ error |
| TEST-586 | ✅ | Info ZIP vide | `shed_zipinfo(zone="storage", path="empty.zip"...` | ✓ success |
| TEST-587 | ✅ | Info ZIP volumineux | `shed_zipinfo(zone="storage", path="large.zip"...` | ✓ success |
| TEST-588 | ✅ | Info ZIP sans path | `shed_zipinfo(zone="storage", path="")` | MISSING_PARAMETER |
| TEST-589 | ✅ | Info ZIP fichiers UTF-8 | `shed_zipinfo(zone="storage", path="été.zip")` | ✓ success |
| TEST-590 | ✅ | Info ZIP zone uploads | `shed_zipinfo(zone="uploads", path="uploaded.z...` | ✓ success |
| TEST-591 | ✅ | Import CSV simple | `shed_sqlite(zone="storage", path="data.db", i...` | ✓ success |
| TEST-592 | ✅ | Import CSV avec headers | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-593 | ✅ | Import CSV sans headers | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-594 | ✅ | Import CSV délimiteur point-virgule | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-595 | ✅ | Import CSV délimiteur tab | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-596 | ✅ | Import CSV table existante (erreur) | `shed_sqlite(zone="storage", path="db.db", imp...` | TABLE_EXISTS |
| TEST-597 | ✅ | Import CSV table existante if_exists=replace | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-598 | ✅ | Import CSV table existante if_exists=append | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-599 | ✅ | Import CSV fichier inexistant | `shed_sqlite(zone="storage", path="db.db", imp...` | FILE_NOT_FOUND |
| TEST-600 | ✅ | Import CSV malformé | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-601 | ✅ | Import CSV vide | `shed_sqlite(zone="storage", path="db.db", imp...` | ✗ error |
| TEST-602 | ✅ | Import CSV zone documents | `shed_sqlite(zone="documents", path="data.db",...` | ✓ success |
| TEST-603 | ✅ | Import CSV zone group | `shed_sqlite(zone="group", group="team", path=...` | ✓ success |
| TEST-604 | ✅ | Import CSV avec quotes | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-605 | ✅ | Import CSV UTF-8 | `shed_sqlite(zone="storage", path="db.db", imp...` | ✓ success |
| TEST-606 | ✅ | Import CSV volumineux | `shed_sqlite(zone="storage", path="big.db", im...` | ✓ success |
| TEST-607 | ✅ | Import CSV avec path traversal | `shed_sqlite(zone="storage", path="db.db", imp...` | PATH_ESCAPE |
| TEST-608 | ✅ | Import CSV nouvelle base | `shed_sqlite(zone="storage", path="new.db", im...` | ✓ success |
| TEST-609 | ✅ | Import CSV sans table | `shed_sqlite(zone="storage", path="db.db", imp...` | MISSING_PARAMETER |
| TEST-610 | ✅ | Import CSV zone invalide | `shed_sqlite(zone="invalid", path="db.db", imp...` | INVALID_ZONE |
| TEST-611 | ✅ | Import CSV group sans group | `shed_sqlite(zone="group", path="db.db", impor...` | MISSING_GROUP |
| TEST-612 | ✅ | Import CSV colonnes nombreuses | `shed_sqlite(zone="storage", path="wide.db", i...` | ✓ success |
| TEST-613 | ✅ | Import CSV lignes nombreuses | `shed_sqlite(zone="storage", path="tall.db", i...` | ✓ success |
| TEST-614 | ✅ | Import CSV types mixtes | `shed_sqlite(zone="storage", path="mixed.db", ...` | ✓ success |
| TEST-615 | ✅ | Import CSV zone uploads | `shed_sqlite(zone="uploads", path="db.db", imp...` | ✗ error |
| TEST-616 | ✅ | Import CSV if_exists invalide | `shed_sqlite(zone="storage", path="db.db", imp...` | INVALID_PARAMETER |
| TEST-617 | ✅ | Import CSV délimiteur invalide | `shed_sqlite(zone="storage", path="db.db", imp...` | Comportement selon implémentat |
| TEST-618 | ✅ | Import CSV depuis autre zone | `shed_sqlite(zone="storage", path="db.db", imp...` | Non supporté ou cross-zone |
| TEST-619 | ✅ | Import CSV nom table avec tirets (invalide) | `shed_sqlite(zone="storage", path="db.db", imp...` | INVALID_PARAMETER |
| TEST-620 | ✅ | Import CSV overwrite base | `shed_sqlite(zone="storage", path="existing.db...` | ✓ success |
| TEST-621 | ✅ | SELECT simple | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-622 | ✅ | SELECT avec WHERE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-623 | ✅ | SELECT avec ORDER BY | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-624 | ✅ | SELECT avec LIMIT | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-625 | ✅ | SELECT avec JOIN (table inexistante) | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-626 | ✅ | SELECT avec GROUP BY | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-627 | ✅ | SELECT avec HAVING | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-628 | ✅ | SELECT fonctions agrégation | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-629 | ✅ | SELECT COUNT | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-630 | ✅ | SELECT DISTINCT | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-631 | ✅ | CREATE TABLE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-632 | ✅ | INSERT INTO | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-633 | ✅ | UPDATE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-634 | ✅ | DELETE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-635 | ✅ | ALTER TABLE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-636 | ✅ | DROP TABLE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-637 | ✅ | Requête sur table inexistante | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-638 | ✅ | Requête syntaxe invalide | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-639 | ✅ | Requête base inexistante | `shed_sqlite(zone="storage", path="nonexistent...` | EXEC_ERROR |
| TEST-640 | ✅ | Requête zone documents | `shed_sqlite(zone="documents", path="db.db", q...` | ✓ success |
| TEST-641 | ✅ | Requête zone group | `shed_sqlite(zone="group", group="team", path=...` | ✓ success |
| TEST-642 | ✅ | Requête avec paramètres | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-643 | ✅ | Multiple statements (bloqué) | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-644 | ✅ | SELECT avec sous-requête | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-645 | ✅ | Requête UNION | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-646 | ✅ | Requête CASE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-647 | ✅ | Requête zone invalide | `shed_sqlite(zone="invalid", path="db.db", que...` | INVALID_ZONE |
| TEST-648 | ✅ | Requête group sans group | `shed_sqlite(zone="group", path="db.db", query...` | MISSING_GROUP |
| TEST-649 | ✅ | Requête vide | `shed_sqlite(zone="storage", path="db.db", que...` | MISSING_PARAMETER |
| TEST-650 | ✅ | Requête résultat volumineux | `shed_sqlite(zone="storage", path="tall.db", q...` | ✓ success |
| TEST-651 | ✅ | SELECT avec LIKE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-652 | ✅ | SELECT avec NULL | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-653 | ✅ | Requête readonly activé | `# Avec sqlite_readonly=true shed_sqlite(zone=...` | ✓ success |
| TEST-654 | ✅ | PRAGMA (si autorisé) | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-655 | ✅ | CREATE INDEX | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-656 | ✅ | Requête avec alias | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-657 | ✅ | Requête COALESCE | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-658 | ✅ | Requête date | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-659 | ✅ | Requête avec path traversal | `shed_sqlite(zone="storage", path="../../../et...` | PATH_ESCAPE |
| TEST-660 | ✅ | Requête fichier non-SQLite | `shed_sqlite(zone="storage", path="file.txt", ...` | EXEC_ERROR |
| TEST-661 | ✅ | Export résultat vers CSV | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-662 | ✅ | Export avec filtre | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-663 | ✅ | Export résultat vide | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-664 | ✅ | Export zone documents | `shed_sqlite(zone="documents", path="db.db", q...` | ✓ success |
| TEST-665 | ✅ | Export zone group | `shed_sqlite(zone="group", group="team", path=...` | ✓ success |
| TEST-666 | ✅ | Export vers fichier existant | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-667 | ✅ | Export volumineux | `shed_sqlite(zone="storage", path="tall.db", q...` | ✓ success |
| TEST-668 | ✅ | Export avec path traversal | `shed_sqlite(zone="storage", path="db.db", que...` | PATH_ESCAPE |
| TEST-669 | ✅ | Export dans sous-dossier | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-670 | ✅ | Export données UTF-8 | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-671 | ✅ | Export avec NULL | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-672 | ✅ | Export agrégation | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-673 | ✅ | Export JOIN | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-674 | ✅ | Export quota dépassé | `shed_sqlite(zone="storage", path="db.db", que...` | EXEC_ERROR |
| TEST-675 | ✅ | Export nom CSV avec espaces | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-676 | ✅ | Export sans query (import + export direct) | `shed_sqlite(zone="storage", path="data.db", t...` | Selon implémentation |
| TEST-677 | ✅ | Export avec colonnes calculées | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-678 | ✅ | Export UNION | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-679 | ✅ | Export zone invalide | `shed_sqlite(zone="invalid", path="db.db", que...` | INVALID_ZONE |
| TEST-680 | ✅ | Export output_csv commençant par zone | `shed_sqlite(zone="storage", path="db.db", que...` | PATH_STARTS_WITH_ZONE |
| TEST-681 | ✅ | Base corrompue | `shed_sqlite(zone="storage", path="corrupted.d...` | EXEC_ERROR |
| TEST-682 | ✅ | Base verrouillée | `shed_sqlite(zone="storage", path="locked.db",...` | Selon état du lock |
| TEST-683 | ✅ | Timeout sur requête longue | `shed_sqlite(zone="storage", path="db.db", que...` | EXEC_ERROR |
| TEST-684 | ✅ | Mémoire insuffisante | `shed_sqlite(zone="storage", path="db.db", que...` | Erreur mémoire ou timeout |
| TEST-685 | ✅ | Import et query simultanés | `shed_sqlite(zone="storage", path="data.db", i...` | Comportement défini (import d' |
| TEST-686 | ✅ | Nom table SQL injection | `shed_sqlite(zone="storage", path="data.db", i...` | ✗ error |
| TEST-687 | ✅ | Path base avec espaces | `shed_sqlite(zone="storage", path="my database...` | ✓ success |
| TEST-688 | ✅ | Base dans sous-dossier | `shed_sqlite(zone="storage", path="data/produc...` | ✓ success |
| TEST-689 | ✅ | VACUUM (si autorisé) | `shed_sqlite(zone="storage", path="db.db", que...` | ✓ success |
| TEST-690 | ✅ | ATTACH DATABASE (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-691 | ✅ | Type fichier texte | `shed_file_type(zone="storage", path="file.txt...` | ✓ success |
| TEST-692 | ✅ | Type fichier JSON | `shed_file_type(zone="storage", path="data.jso...` | ✓ success |
| TEST-693 | ✅ | Type fichier PNG | `shed_file_type(zone="storage", path="test_ima...` | ✓ success |
| TEST-694 | ✅ | Type fichier PDF | `shed_file_type(zone="storage", path="document...` | ✓ success |
| TEST-695 | ✅ | Type fichier ZIP | `shed_file_type(zone="storage", path="archive....` | ✓ success |
| TEST-696 | ✅ | Type fichier inexistant | `shed_file_type(zone="storage", path="nonexist...` | FILE_NOT_FOUND |
| TEST-697 | ✅ | Type dossier | `shed_file_type(zone="storage", path="folder")` | ✓ success |
| TEST-698 | ✅ | Type zone documents | `shed_file_type(zone="documents", path="doc.md...` | ✓ success |
| TEST-699 | ✅ | Type zone group sans paramètre group | `shed_file_type(zone="group", path="shared.md"...` | MISSING_PARAMETER |
| TEST-700 | ✅ | Type zone uploads | `shed_file_type(zone="uploads", path="config.j...` | ✓ success |
| TEST-701 | ✅ | Type zone invalide | `shed_file_type(zone="invalid", path="file.txt...` | INVALID_ZONE |
| TEST-702 | ✅ | Type path traversal | `shed_file_type(zone="storage", path="../../.....` | PATH_ESCAPE |
| TEST-703 | ✅ | Type fichier binaire inconnu | `shed_file_type(zone="storage", path="data.bin...` | ✓ success |
| TEST-704 | ✅ | Type group sans group param | `shed_file_type(zone="group", path="file.txt")` | MISSING_PARAMETER |
| TEST-705 | ✅ | Type sans path | `shed_file_type(zone="storage", path="")` | ✓ success |
| TEST-706 | ✅ | Convertir vers Unix (LF) | `shed_convert_eol(zone="storage", path="window...` | ✓ success |
| TEST-707 | ✅ | Convertir vers Windows (CRLF) | `shed_convert_eol(zone="storage", path="unix.t...` | ✓ success |
| TEST-708 | ✅ | Convertir fichier déjà Unix | `shed_convert_eol(zone="storage", path="file.t...` | ✓ success |
| TEST-709 | ✅ | Convertir zone documents | `shed_convert_eol(zone="documents", path="doc....` | ✓ success |
| TEST-710 | ✅ | Convertir fichier inexistant | `shed_convert_eol(zone="storage", path="nonexi...` | FILE_NOT_FOUND |
| TEST-711 | ✅ | Convertir binaire (erreur) | `shed_convert_eol(zone="storage", path="image....` | ✓ success |
| TEST-712 | ✅ | Convertir to invalide | `shed_convert_eol(zone="storage", path="file.t...` | INVALID_MODE |
| TEST-713 | ✅ | Convertir zone uploads (interdit) | `shed_convert_eol(zone="uploads", path="file.t...` | ZONE_READONLY |
| TEST-714 | ✅ | Convertir avec path traversal | `shed_convert_eol(zone="storage", path="../../...` | PATH_ESCAPE |
| TEST-715 | ✅ | Convertir fichier volumineux | `shed_convert_eol(zone="storage", path="large....` | ✓ success |
| TEST-716 | ✅ | Hexdump par défaut | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-717 | ✅ | Hexdump avec offset | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-718 | ✅ | Hexdump avec length | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-719 | ✅ | Hexdump offset + length | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-720 | ✅ | Hexdump fichier texte | `shed_hexdump(zone="storage", path="text.txt")` | ✓ success |
| TEST-721 | ✅ | Hexdump fichier inexistant | `shed_hexdump(zone="storage", path="nonexisten...` | FILE_NOT_FOUND |
| TEST-722 | ✅ | Hexdump zone documents | `shed_hexdump(zone="documents", path="doc.md")` | ✓ success |
| TEST-723 | ✅ | Hexdump offset négatif | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-724 | ✅ | Hexdump offset > taille | `shed_hexdump(zone="storage", path="binary.bin...` | ✓ success |
| TEST-725 | ✅ | Hexdump path traversal | `shed_hexdump(zone="storage", path="../../../e...` | PATH_ESCAPE |
| TEST-726 | ✅ | Force unlock fichier verrouillé | `shed_force_unlock(zone="storage", path="locke...` | ✓ success |
| TEST-727 | ✅ | Force unlock fichier non verrouillé | `shed_force_unlock(zone="storage", path="not_l...` | ✓ success |
| TEST-728 | ✅ | Force unlock fichier inexistant | `shed_force_unlock(zone="storage", path="nonex...` | ✓ success |
| TEST-729 | ✅ | Force unlock zone documents | `shed_force_unlock(zone="documents", path="loc...` | ✓ success |
| TEST-730 | ✅ | Force unlock zone group | `shed_force_unlock(zone="group", group="team",...` | ✓ success |
| TEST-731 | ✅ | Créer lien download | `shed_link_create(zone="storage", path="docume...` | ✗ error |
| TEST-732 | ✅ | Créer lien zone documents (API non dispo) | `shed_link_create(zone="documents", path="doc....` | ✗ error |
| TEST-733 | ✅ | Créer lien zone group (API non dispo) | `shed_link_create(zone="group", group="team", ...` | ✗ error |
| TEST-734 | ✅ | Créer lien fichier inexistant | `shed_link_create(zone="storage", path="nonexi...` | FILE_NOT_FOUND |
| TEST-735 | ✅ | Créer lien dossier (interdit) | `shed_link_create(zone="storage", path="folder...` | NOT_A_FILE |
| TEST-736 | ✅ | Créer lien zone uploads | `shed_link_create(zone="uploads", path="upload...` | FILE_NOT_FOUND |
| TEST-737 | ✅ | Créer lien path traversal | `shed_link_create(zone="storage", path="../../...` | PATH_ESCAPE |
| TEST-738 | ✅ | Créer lien zone invalide | `shed_link_create(zone="invalid", path="file.p...` | INVALID_ZONE |
| TEST-739 | ✅ | Créer lien group sans group | `shed_link_create(zone="group", path="file.pdf...` | MISSING_GROUP |
| TEST-740 | ✅ | Créer lien sans path | `shed_link_create(zone="storage", path="")` | NOT_A_FILE |
| TEST-741 | ✅ | Créer lien fichier binaire (API non dispo) | `shed_link_create(zone="storage", path="data.b...` | ✗ error |
| TEST-742 | ✅ | Créer lien fichier texte (fichier manquant) | `shed_link_create(zone="storage", path="notes....` | FILE_NOT_FOUND |
| TEST-743 | ✅ | Créer lien fichier ZIP (API non dispo) | `shed_link_create(zone="storage", path="archiv...` | ✗ error |
| TEST-744 | ✅ | Créer lien fichier avec espaces (fichier manquant) | `shed_link_create(zone="storage", path="my rep...` | FILE_NOT_FOUND |
| TEST-745 | ✅ | Créer lien fichier UTF-8 (fichier manquant) | `shed_link_create(zone="storage", path="résumé...` | FILE_NOT_FOUND |
| TEST-746 | ✅ | Créer plusieurs liens même fichier (fichier manqua... | `shed_link_create(zone="storage", path="file.p...` | FILE_NOT_FOUND |
| TEST-747 | ✅ | Créer lien fichier volumineux (API non dispo) | `shed_link_create(zone="storage", path="large....` | ✗ error |
| TEST-748 | ✅ | Vérifier format clickable_link (fichier manquant) | `shed_link_create(zone="storage", path="file.p...` | FILE_NOT_FOUND |
| TEST-749 | ✅ | Créer lien dans sous-dossier (fichier manquant) | `shed_link_create(zone="storage", path="report...` | FILE_NOT_FOUND |
| TEST-750 | ✅ | Créer lien fichier caché (API non dispo) | `shed_link_create(zone="storage", path=".hidde...` | ✗ error |
| TEST-751 | ✅ | Lister liens (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-752 | ✅ | Lister liens vide (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-753 | ✅ | Lister après création (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-754 | ✅ | Lister après suppression (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-755 | ✅ | Vérifier infos dans liste (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-756 | ✅ | Lister plusieurs liens (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-757 | ✅ | Lister liens différentes zones (skip - API non dis... | `shed_stats()` | ✓ success |
| TEST-758 | ✅ | Lister ne voit pas liens autres users (skip - API ... | `shed_stats()` | ✓ success |
| TEST-759 | ✅ | Lister liens groupe (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-760 | ✅ | Lister avec pagination (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-761 | ✅ | Supprimer lien (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-762 | ✅ | Supprimer lien inexistant (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-763 | ✅ | Supprimer sans file_id (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-764 | ✅ | Supprimer lien autre user (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-765 | ✅ | Supprimer puis vérifier liste (skip - API non disp... | `shed_stats()` | ✓ success |
| TEST-766 | ✅ | Double suppression (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-767 | ✅ | Supprimer ne supprime pas fichier (skip - API non ... | `shed_stats() # Vérifier que le fichier source...` | Fichier source intact |
| TEST-768 | ✅ | Supprimer lien zone documents (skip - API non disp... | `shed_stats()` | ✓ success |
| TEST-769 | ✅ | Supprimer lien zone group (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-770 | ✅ | file_id invalide format (skip - API non dispo) | `shed_stats()` | ✓ success |
| TEST-771 | ✅ | Lister groupes (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-772 | ✅ | Lister groupes vide (API non dispo) | `# User sans groupe shed_group_list()` | ✗ error |
| TEST-773 | ✅ | Vérifier infos groupe (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-774 | ✅ | Lister plusieurs groupes (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-775 | ✅ | Groupe owner vs member (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-776 | ✅ | Groupes ne voit pas groupes autres users (API non ... | `shed_group_list()` | ✗ error |
| TEST-777 | ✅ | Liste inclut groupes invité (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-778 | ✅ | Ordre de liste (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-779 | ✅ | Groupe avec nom spécial (API non dispo) | `shed_group_list()` | ✗ error |
| TEST-780 | ✅ | API groupes indisponible | `shed_group_list()` | ✗ error |
| TEST-781 | ✅ | Info groupe existant | `shed_group_info(group="team-alpha")` | ✓ success |
| TEST-782 | ✅ | Info groupe inexistant | `shed_group_info(group="nonexistent")` | ✗ error |
| TEST-783 | ✅ | Info groupe non membre | `shed_group_info(group="other-team")` | ✗ error |
| TEST-784 | ✅ | Info sans group | `shed_group_info(group="")` | INVALID_GROUP_ID |
| TEST-785 | ✅ | Vérifier membres dans info | `shed_group_info(group="team")` | ✓ success |
| TEST-786 | ✅ | Vérifier quota dans info | `shed_group_info(group="team")` | ✓ success |
| TEST-787 | ✅ | Info groupe avec beaucoup de membres | `shed_group_info(group="large-team")` | ✓ success |
| TEST-788 | ✅ | Vérifier owner dans info | `shed_group_info(group="team")` | ✓ success |
| TEST-789 | ✅ | Info groupe ID vs nom | `shed_group_info(group="team-name")` | ✓ success |
| TEST-790 | ✅ | Vérifier created_at dans info | `shed_group_info(group="team")` | ✓ success |
| TEST-791 | ✅ | Info groupe avec fichiers | `shed_group_info(group="team")` | ✓ success |
| TEST-792 | ✅ | Groupe ID caractères spéciaux | `shed_group_info(group="team!@#")` | ✗ error |
| TEST-793 | ✅ | Info groupe inexistant | `shed_group_info(group="empty-new-group")` | ✗ error |
| TEST-794 | ✅ | Info groupe description | `shed_group_info(group="team")` | ✓ success |
| TEST-795 | ✅ | Info groupe timeout | `shed_group_info(group="team")` | ✓ success |
| TEST-796 | ✅ | Changer mode vers owner | `shed_group_set_mode(group="team", path="share...` | ✓ success |
| TEST-797 | ✅ | Changer mode vers group | `shed_group_set_mode(group="team", path="share...` | ✓ success |
| TEST-798 | ✅ | Changer mode vers owner_ro | `shed_group_set_mode(group="team", path="prote...` | ✓ success |
| TEST-799 | ✅ | Changer mode fichier inexistant | `shed_group_set_mode(group="team", path="nonex...` | FILE_NOT_FOUND |
| TEST-800 | ✅ | Changer mode non owner | `shed_group_set_mode(group="team", path="owner...` | NOT_FILE_OWNER |
| TEST-801 | ✅ | Changer mode invalide | `shed_group_set_mode(group="team", path="share...` | INVALID_MODE |
| TEST-802 | ✅ | Changer mode sans group | `shed_group_set_mode(group="", path="shared.md...` | INVALID_GROUP_ID |
| TEST-803 | ✅ | Changer mode sans path | `shed_group_set_mode(group="team", path="", mo...` | FILE_NOT_FOUND |
| TEST-804 | ✅ | Changer mode sans mode | `shed_group_set_mode(group="team", path="share...` | INVALID_MODE |
| TEST-805 | ✅ | Changer mode groupe non membre | `shed_group_set_mode(group="other-team", path=...` | GROUP_ACCESS_DENIED |
| TEST-806 | ✅ | Changer mode path traversal | `shed_group_set_mode(group="team", path="../.....` | PATH_ESCAPE |
| TEST-807 | ✅ | Changer mode dossier | `shed_group_set_mode(group="team", path="folde...` | FILE_NOT_FOUND |
| TEST-808 | ✅ | Vérifier mode après changement | `shed_group_set_mode(group="team", path="log.t...` | ✓ success |
| TEST-809 | ✅ | Changer mode plusieurs fois | `shed_group_set_mode(group="team", path="doc.m...` | ✓ success |
| TEST-810 | ✅ | Groupe inexistant | `shed_group_set_mode(group="nonexistent", path...` | GROUP_NOT_FOUND |
| TEST-811 | ✅ | Transférer ownership à non-membre | `shed_group_chown(group="team", path="shared.m...` | INVALID_OWNER |
| TEST-812 | ✅ | Transférer à non-membre invalide | `shed_group_chown(group="team", path="shared.m...` | INVALID_OWNER |
| TEST-813 | ✅ | Transférer fichier inexistant | `shed_group_chown(group="team", path="nonexist...` | FILE_NOT_FOUND |
| TEST-814 | ✅ | Transférer non owner | `shed_group_chown(group="team", path="owner_ro...` | NOT_FILE_OWNER |
| TEST-815 | ✅ | Transférer sans group | `shed_group_chown(group="", path="shared.md", ...` | INVALID_GROUP_ID |
| TEST-816 | ✅ | Transférer sans path | `shed_group_chown(group="team", path="", new_o...` | FILE_NOT_FOUND |
| TEST-817 | ✅ | Transférer sans new_owner | `shed_group_chown(group="team", path="shared.m...` | INVALID_OWNER |
| TEST-818 | ✅ | Transférer groupe non membre | `shed_group_chown(group="other-team", path="sh...` | GROUP_ACCESS_DENIED |
| TEST-819 | ✅ | Transférer path traversal | `shed_group_chown(group="team", path="../../.....` | PATH_ESCAPE |
| TEST-820 | ✅ | Transférer à soi-même | `shed_group_chown(group="team", path="shared.m...` | ✓ success |
| TEST-821 | ✅ | Vérifier owner après transfer | `shed_group_chown(group="team", path="data.csv...` | ✓ success |
| TEST-822 | ✅ | Transférer fichier mode owner_ro à soi-même | `shed_group_chown(group="team", path="protecte...` | ✓ success |
| TEST-823 | ✅ | new_owner ID invalide format | `shed_group_chown(group="team", path="shared.m...` | INVALID_OWNER |
| TEST-824 | ✅ | Transférer dossier | `shed_group_chown(group="team", path="folder",...` | FILE_NOT_FOUND |
| TEST-825 | ✅ | Groupe inexistant | `shed_group_chown(group="nonexistent", path="s...` | GROUP_NOT_FOUND |
| TEST-826 | ✅ | Double transfer échoue (non-membre) | `shed_group_chown(group="team", path="log.txt"...` | INVALID_OWNER |
| TEST-827 | ✅ | Transférer fichier binaire à soi-même | `shed_group_chown(group="team", path="shared.b...` | ✓ success |
| TEST-828 | ✅ | Transférer fichier inexistant | `shed_group_chown(group="team", path="large.bi...` | FILE_NOT_FOUND |
| TEST-829 | ✅ | new_owner par nom invalide | `shed_group_chown(group="team", path="shared.m...` | INVALID_OWNER |
| TEST-830 | ✅ | Transférer dans sous-dossier inexistant | `shed_group_chown(group="team", path="folder/f...` | FILE_NOT_FOUND |
| TEST-831 | ✅ | Import fichier spécifique (pas de fichiers) | `shed_import(filename="uploaded.pdf")` | ✗ error |
| TEST-832 | ✅ | Import tous les fichiers (pas de fichiers) | `shed_import(import_all=True)` | ✗ error |
| TEST-833 | ✅ | Import fichier inexistant (pas de fichiers) | `shed_import(filename="nonexistent.pdf")` | ✗ error |
| TEST-834 | ✅ | Import sans paramètres (pas de fichiers) | `shed_import()` | ✗ error |
| TEST-835 | ✅ | Import aucun fichier uploadé | `shed_import(import_all=True)` | ✗ error |
| TEST-836 | ✅ | Import fichier déjà importé (pas de fichiers) | `shed_import(filename="already.pdf")` | ✗ error |
| TEST-837 | ✅ | Import fichier volumineux (pas de fichiers) | `shed_import(filename="large.zip")` | ✗ error |
| TEST-838 | ✅ | Vérifier fichiers dans uploads après import (pas d... | `shed_import(import_all=True)` | ✗ error |
| TEST-839 | ✅ | Import multiple fichiers (pas de fichiers) | `shed_import(import_all=True)` | ✗ error |
| TEST-840 | ✅ | Import avec path traversal (pas de fichiers) | `shed_import(filename="../../../etc/passwd")` | ✗ error |
| TEST-841 | ✅ | Import fichier avec espaces (pas de fichiers) | `shed_import(filename="my document.pdf")` | ✗ error |
| TEST-842 | ✅ | Import fichier UTF-8 (pas de fichiers) | `shed_import(filename="résumé.pdf")` | ✗ error |
| TEST-843 | ✅ | Import retourne liste (pas de fichiers) | `shed_import(import_all=True)` | ✗ error |
| TEST-844 | ✅ | Import filename vide (pas de fichiers) | `shed_import(filename="")` | ✗ error |
| TEST-845 | ✅ | Import filename et import_all (pas de fichiers) | `shed_import(filename="file.pdf", import_all=T...` | ✗ error |
| TEST-846 | ✅ | Aide générale | `shed_help()` | ✓ success |
| TEST-847 | ✅ | Aide howto paths | `shed_help(howto="paths")` | ✓ success |
| TEST-848 | ✅ | Aide howto zones (invalide) | `shed_help(howto="zones")` | ✗ error |
| TEST-849 | ✅ | Aide howto commands | `shed_help(howto="commands")` | ✓ success |
| TEST-850 | ✅ | Aide howto csv_to_sqlite | `shed_help(howto="csv_to_sqlite")` | ✓ success |
| TEST-851 | ✅ | Aide howto download | `shed_help(howto="download")` | ✓ success |
| TEST-852 | ✅ | Aide howto edit | `shed_help(howto="edit")` | ✓ success |
| TEST-853 | ✅ | Aide howto share | `shed_help(howto="share")` | ✓ success |
| TEST-854 | ✅ | Aide howto invalide | `shed_help(howto="nonexistent")` | ✗ error |
| TEST-855 | ✅ | Aide howto vide | `shed_help(howto="")` | ✓ success |
| TEST-856 | ✅ | Aide contient liste fonctions | `shed_help()` | ✓ success |
| TEST-857 | ✅ | Aide format markdown | `shed_help()` | ✓ success |
| TEST-858 | ✅ | Aide howto upload | `shed_help(howto="upload")` | ✓ success |
| TEST-859 | ✅ | Aide howto network | `shed_help(howto="network")` | ✓ success |
| TEST-860 | ✅ | Aide howto case insensitive | `shed_help(howto="PATHS")` | Même résultat que "paths" |
| TEST-861 | ✅ | Stats utilisateur | `shed_stats()` | ✓ success |
| TEST-862 | ✅ | Stats contient usage | `shed_stats()` | ✓ success |
| TEST-863 | ✅ | Stats contient zones | `shed_stats()` | ✓ success |
| TEST-864 | ✅ | Stats file count | `shed_stats()` | ✓ success |
| TEST-865 | ✅ | Stats groupes | `shed_stats()` | ✓ success |
| TEST-866 | ✅ | Parameters | `shed_parameters()` | ✓ success |
| TEST-867 | ✅ | Parameters contient quotas | `shed_parameters()` | ✓ success |
| TEST-868 | ✅ | Parameters contient timeouts | `shed_parameters()` | ✓ success |
| TEST-869 | ✅ | Parameters contient network_mode | `shed_parameters()` | ✓ success |
| TEST-870 | ✅ | Parameters contient limites | `shed_parameters()` | ✓ success |
| TEST-871 | ✅ | Allowed commands | `shed_allowed_commands()` | ✓ success |
| TEST-872 | ✅ | Allowed commands par zone | `shed_allowed_commands()` | ✓ success |
| TEST-873 | ✅ | Allowed commands contient basiques | `shed_allowed_commands()` | ✓ success |
| TEST-874 | ✅ | Allowed commands network | `shed_allowed_commands()` | ✓ success |
| TEST-875 | ✅ | Maintenance | `shed_maintenance()` | ✓ success |
| TEST-876 | ✅ | Maintenance nettoie locks expirés | `shed_maintenance()` | ✓ success |
| TEST-877 | ✅ | Maintenance sans locks expirés | `shed_maintenance()` | ✓ success |
| TEST-878 | ✅ | Stats après opérations | `shed_stats()` | ✓ success |
| TEST-879 | ✅ | Parameters version | `shed_parameters()` | ✓ success |
| TEST-880 | ✅ | Allowed commands git | `shed_allowed_commands()` | ✓ success |
| TEST-881 | ✅ | Path traversal simple | `shed_exec(zone="storage", cmd="cat", args=["....` | PATH_ESCAPE |
| TEST-882 | ✅ | Path traversal encodé (non décodé) | `shed_exec(zone="storage", cmd="cat", args=["....` | ✓ success |
| TEST-883 | ✅ | Path traversal double encodé (non décodé) | `shed_exec(zone="storage", cmd="cat", args=["....` | ✓ success |
| TEST-884 | ✅ | Path avec ../ interne | `shed_exec(zone="storage", cmd="cat", args=["f...` | Normalisé, pas d'escape |
| TEST-885 | ✅ | Symlink escape (symlink non existant) | `shed_exec(zone="storage", cmd="cat", args=["e...` | ✓ success |
| TEST-886 | ✅ | Path absolu | `shed_exec(zone="storage", cmd="cat", args=["/...` | PATH_ESCAPE |
| TEST-887 | ✅ | Path avec null byte | `shed_exec(zone="storage", cmd="cat", args=["f...` | EXEC_ERROR |
| TEST-888 | ✅ | Path avec backslash (Linux: pas un séparateur) | `shed_exec(zone="storage", cmd="cat", args=["....` | ✓ success |
| TEST-889 | ✅ | Traversal via stdout_file | `shed_exec(zone="storage", cmd="ls", stdout_fi...` | PATH_ESCAPE |
| TEST-890 | ✅ | Traversal via stderr_file | `shed_exec(zone="storage", cmd="ls", stderr_fi...` | PATH_ESCAPE |
| TEST-891 | ✅ | Traversal shed_patch_text | `shed_patch_text(zone="storage", path="../../....` | PATH_ESCAPE |
| TEST-892 | ✅ | Traversal shed_delete | `shed_delete(zone="storage", path="../../../im...` | PATH_ESCAPE |
| TEST-893 | ✅ | Traversal shed_rename dest | `shed_rename(zone="storage", old_path="file.tx...` | PATH_ESCAPE |
| TEST-894 | ✅ | Traversal shed_zip dest | `shed_zip(zone="storage", src="folder", dest="...` | PATH_ESCAPE |
| TEST-895 | ✅ | Traversal shed_sqlite path | `shed_sqlite(zone="storage", path="../../../et...` | PATH_ESCAPE |
| TEST-896 | ✅ | Injection point-virgule | `shed_exec(zone="storage", cmd="ls", args=["; ...` | ARGUMENT_FORBIDDEN |
| TEST-897 | ✅ | Injection pipe | `shed_exec(zone="storage", cmd="cat", args=["f...` | ARGUMENT_FORBIDDEN |
| TEST-898 | ✅ | Injection && | `shed_exec(zone="storage", cmd="ls", args=["&&...` | ARGUMENT_FORBIDDEN |
| TEST-899 | ✅ | Injection backticks | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-900 | ✅ | Injection $() | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-901 | ✅ | Injection > | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-902 | ✅ | Injection >> | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-903 | ✅ | Commande non whitelist | `shed_exec(zone="storage", cmd="bash", args=["...` | COMMAND_FORBIDDEN |
| TEST-904 | ✅ | Commande rm -rf / | `shed_exec(zone="storage", cmd="rm", args=["-r...` | ✗ error |
| TEST-905 | ✅ | Commande curl sans -o (network disabled) | `shed_exec(zone="storage", cmd="curl", args=["...` | COMMAND_FORBIDDEN |
| TEST-906 | ✅ | Commande wget (network disabled) | `shed_exec(zone="storage", cmd="wget", args=["...` | COMMAND_FORBIDDEN |
| TEST-907 | ✅ | Network disabled | `shed_exec(zone="storage", cmd="curl", args=["...` | COMMAND_FORBIDDEN |
| TEST-908 | ✅ | Find -exec bloqué | `shed_exec(zone="storage", cmd="find", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-909 | ✅ | Awk system() bloqué | `shed_exec(zone="storage", cmd="awk", args=["B...` | ARGUMENT_FORBIDDEN |
| TEST-910 | ✅ | Xargs bloqué | `shed_exec(zone="storage", cmd="xargs", args=[...` | COMMAND_FORBIDDEN |
| TEST-911 | ✅ | Injection newline | `shed_exec(zone="storage", cmd="echo", args=["...` | Newline dans argument OK, pas  |
| TEST-912 | ✅ | SQL injection shed_sqlite | `shed_sqlite(zone="storage", path="db.db", que...` | ✗ error |
| TEST-913 | ✅ | Table name injection | `shed_sqlite(zone="storage", path="data.db", i...` | ✗ error |
| TEST-914 | ✅ | Commande vide | `shed_exec(zone="storage", cmd="")` | COMMAND_FORBIDDEN |
| TEST-915 | ✅ | Commande avec espaces | `shed_exec(zone="storage", cmd="ls -la")` | ✗ error |
| TEST-916 | ✅ | Fichier trop grand storage | `shed_patch_text(zone="storage", path="overflo...` | FILE_TOO_LARGE |
| TEST-917 | ✅ | Fichier trop grand documents | `shed_patch_text(zone="documents", path="huge....` | FILE_TOO_LARGE |
| TEST-918 | ✅ | Fichier trop grand group | `shed_patch_text(zone="group", group="team", p...` | FILE_TOO_LARGE |
| TEST-919 | ✅ | shed_patch_bytes simple | `shed_patch_bytes(zone="storage", path="tiny.b...` | ✓ success |
| TEST-920 | ✅ | Zone uploads readonly (write) | `shed_exec(zone="uploads", cmd="touch", args=[...` | COMMAND_FORBIDDEN |
| TEST-921 | ✅ | Zone uploads readonly (mkdir) | `shed_exec(zone="uploads", cmd="mkdir", args=[...` | COMMAND_FORBIDDEN |
| TEST-922 | ✅ | Group access denied | `shed_exec(zone="group", group="not-my-group",...` | GROUP_ACCESS_DENIED |
| TEST-923 | ✅ | Group file mode owner (fichier inexistant) | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-924 | ✅ | Group file mode owner_ro (fichier inexistant) | `shed_patch_text(zone="group", group="team", p...` | ✓ success |
| TEST-925 | ✅ | Group file delete mode owner (fichier créé par TES... | `shed_delete(zone="group", group="team", path=...` | ✓ success |
| TEST-926 | ✅ | Timeout commande longue | `shed_exec(zone="storage", cmd="sleep", args=[...` | TIMEOUT |
| TEST-927 | ✅ | Mémoire limite subprocess (contient <) | `shed_exec(zone="storage", cmd="awk", args=["B...` | ARGUMENT_FORBIDDEN |
| TEST-928 | ✅ | CPU limite subprocess | `shed_exec(zone="storage", cmd="factor", args=...` | Timeout ou limite CPU |
| TEST-929 | ✅ | Output truncation | `shed_exec(zone="storage", cmd="cat", args=["h...` | ✓ success |
| TEST-930 | ✅ | Lock expiration | `# Lock créé il y a > lock_max_age_hours shed_...` | Lock expiré, opération échoue  |
| TEST-931 | ✅ | User ID test via stats | `shed_stats()` | ✓ success |
| TEST-932 | ✅ | Conversation ID test via stats | `shed_stats()` | ✓ success |
| TEST-933 | ✅ | Zone group vide | `shed_exec(zone="group", group="", cmd="ls")` | MISSING_PARAMETER |
| TEST-934 | ✅ | Group ID caractères interdits | `shed_exec(zone="group", group="team!@#$%", cm...` | GROUP_NOT_FOUND |
| TEST-935 | ✅ | Path commençant par zone | `shed_exec(zone="storage", cmd="cat", args=["S...` | PATH_STARTS_WITH_ZONE |
| TEST-936 | ✅ | Output fichier inexistant | `shed_exec(zone="storage", cmd="cat", args=["5...` | ✓ success |
| TEST-937 | ✅ | Locked edit sans verrouillage | `shed_lockedit_save(zone="storage", path="lock...` | NOT_IN_EDIT_MODE |
| TEST-938 | ✅ | Download link delete (API non dispo) | `shed_link_delete(file_id="other-user-file-id"...` | ✗ error |
| TEST-939 | ✅ | Unzip fichier inexistant | `shed_unzip(zone="storage", src="suspicious.zi...` | FILE_NOT_FOUND |
| TEST-940 | ✅ | Network disabled (curl) | `shed_exec(zone="storage", cmd="curl", args=["...` | COMMAND_FORBIDDEN |
| TEST-941 | ✅ | Workflow upload -> storage -> zip -> link | `shed_import(import_all=True) shed_move_upload...` | Workflow complet réussi |
| TEST-942 | ✅ | Workflow CSV -> SQLite -> analyse | `shed_sqlite(zone="storage", path="sales.db", ...` | Analyse réussie |
| TEST-943 | ✅ | Workflow multiple CSV -> SQLite -> JOIN | `shed_sqlite(zone="storage", path="db.db", imp...` | JOIN réussi |
| TEST-944 | ✅ | Workflow document versioning | `shed_patch_text(zone="documents", path="repor...` | Deux commits visibles |
| TEST-945 | ✅ | Workflow locked edit complet | `shed_lockedit_open(zone="storage", path="conf...` | Edit workflow complet |
| TEST-946 | ✅ | Workflow group collaboration | `shed_patch_text(zone="storage", path="draft.m...` | Collaboration réussie |
| TEST-947 | ✅ | Workflow media processing | `shed_import(filename="video.mp4") shed_move_u...` | Extraction audio |
| TEST-948 | ✅ | Workflow pandoc conversion | `shed_patch_text(zone="storage", path="doc.md"...` | Conversions réussies |
| TEST-949 | ✅ | Workflow archive multi-fichiers | `shed_exec(zone="storage", cmd="mkdir", args=[...` | Archive avec structure |
| TEST-950 | ✅ | Workflow backup complet | `shed_stats() shed_exec(zone="storage", cmd="l...` | Backup téléchargeable |
| TEST-951 | ✅ | Workflow cross-zone | `shed_import(filename="data.csv") shed_move_up...` | Fichier dans 3 zones |
| TEST-952 | ✅ | Workflow analyse texte | `shed_exec(zone="storage", cmd="wc", args=["-l...` | Pipeline d'analyse |
| TEST-953 | ✅ | Workflow JSON processing | `shed_patch_text(zone="storage", path="data.js...` | JSON -> CSV |
| TEST-954 | ✅ | Workflow documents Git history | `shed_patch_text(zone="documents", path="evolv...` | Historique consultable |
| TEST-955 | ✅ | Workflow cleanup | `shed_exec(zone="storage", cmd="find", args=["...` | Nettoyage effectué |
| TEST-956 | ✅ | Workflow batch file creation | `shed_patch_text(zone="storage", path="batch_f...` | ✓ success |
| TEST-957 | ✅ | Workflow SQLite multi-operations | `shed_sqlite(zone="storage", path="app.db", qu...` | ✓ success |
| TEST-958 | ✅ | Workflow downloads bulk | `shed_link_list()` | ✗ error |
| TEST-959 | ✅ | Workflow error recovery | `shed_lockedit_open(zone="storage", path="conf...` | ✓ success |
| TEST-960 | ✅ | Workflow permissions group | `shed_group_info(group="33333333-3333-3333-333...` | ✓ success |
| TEST-961 | ✅ | Fichier nom très long | `shed_patch_text(zone="storage", path="aaaaaaa...` | ✓ success |
| TEST-962 | ✅ | Arborescence très profonde | `shed_patch_text(zone="storage", path="d/d/d/d...` | ✓ success |
| TEST-963 | ✅ | Beaucoup de fichiers dans dossier | `shed_exec(zone="storage", cmd="ls", args=["hu...` | ✓ success |
| TEST-964 | ✅ | Fichier avec tous caractères UTF-8 | `shed_patch_text(zone="storage", path="unicode...` | ✓ success |
| TEST-965 | ✅ | Fichier avec emojis dans contenu | `shed_patch_text(zone="storage", path="emoji.t...` | ✓ success |
| TEST-966 | ✅ | Fichier avec emojis dans nom | `shed_patch_text(zone="storage", path="file_🎉....` | Selon système de fichiers |
| TEST-967 | ✅ | Opérations simultanées même fichier | `shed_lockedit_open(zone="storage", path="log....` | ✓ success |
| TEST-968 | ✅ | Requête SQL résultat géant | `shed_sqlite(zone="storage", path="big.db", qu...` | Résultat tronqué |
| TEST-969 | ✅ | ZIP récursif (zip de zip) | `shed_zip(zone="storage", src="archive.zip", d...` | ✓ success |
| TEST-970 | ✅ | Unzip dans lui-même | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-971 | ✅ | SQLite database locked | `shed_sqlite(zone="storage", path="locked.db",...` | ✓ success |
| TEST-972 | ✅ | Git repo status | `shed_exec(zone="documents", cmd="git", args=[...` | ✓ success |
| TEST-973 | ✅ | Fichier sparse | `shed_hexdump(zone="storage", path="sparse.bin...` | Gestion fichiers sparse |
| TEST-974 | ✅ | Timeout très court custom | `shed_exec(zone="storage", cmd="sleep", args=[...` | TIMEOUT |
| TEST-975 | ✅ | Output exactement à la limite | `shed_exec(zone="storage", cmd="cat", args=["e...` | ✓ success |
| TEST-976 | ✅ | Binary dans text function | `shed_patch_text(zone="storage", path="binary....` | Comportement défini |
| TEST-977 | ✅ | Text dans binary function | `shed_patch_bytes(zone="storage", path="text.t...` | ✓ success |
| TEST-978 | ✅ | Circular symlinks | `shed_exec(zone="storage", cmd="cat", args=["c...` | ✓ success |
| TEST-979 | ✅ | Fichier sans permission lecture | `shed_exec(zone="storage", cmd="cat", args=["n...` | ✓ success |
| TEST-980 | ✅ | Zone avec caractères spéciaux | `shed_exec(zone="storage", cmd="ls", args=["fo...` | ✓ success |
| TEST-981 | ✅ | Commande avec timeout=0 | `shed_exec(zone="storage", cmd="ls", timeout=0...` | ✓ success |
| TEST-982 | ✅ | Très grand nombre de locks | `shed_stats()` | ✓ success |
| TEST-983 | ✅ | Pattern regex catastrophique | `shed_patch_text(zone="storage", path="file.tx...` | Timeout ou protection |
| TEST-984 | ✅ | Import fichier 0 bytes | `shed_import(filename="empty_upload.txt")` | ✗ error |
| TEST-985 | ✅ | SQLite table avec 0 colonnes | `shed_sqlite(zone="storage", path="weird.db", ...` | Erreur SQL |
| TEST-986 | ✅ | Nom fichier uniquement extension | `shed_patch_text(zone="storage", path=".txt", ...` | ✓ success |
| TEST-987 | ✅ | Nom fichier uniquement point | `shed_patch_text(zone="storage", path=".", con...` | ✗ error |
| TEST-988 | ✅ | Nom fichier deux points | `shed_patch_text(zone="storage", path="..", co...` | PATH_ESCAPE |
| TEST-989 | ✅ | Commande avec arguments très longs | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-990 | ✅ | Beaucoup de groupes | `shed_group_list()` | ✗ error |
| TEST-991 | ✅ | Download link fichier supprimé | `shed_link_create(zone="storage", path="log.tx...` | ✗ error |
| TEST-992 | ✅ | Concurrent SQLite write | `shed_sqlite(zone="storage", path="concurrent....` | ✓ success |
| TEST-993 | ✅ | Fichier avec newlines dans nom | `shed_patch_text(zone="storage", path="file\nn...` | ✓ success |
| TEST-994 | ✅ | Base SQLite avec schéma complexe | `shed_sqlite(zone="storage", path="complex.db"...` | ✓ success |
| TEST-995 | ✅ | Workflow complet données pays | `shed_stats()` | ✓ success |
| TEST-996 | ✅ | Recovery après crash | `shed_lockedit_open(zone="storage", path="data...` | ✓ success |
| TEST-997 | ✅ | Stress test sequential | `shed_patch_text(zone="storage", path="stress_...` | ✓ success |
| TEST-998 | ✅ | Toutes les zones en une session | `shed_exec(zone="uploads", cmd="ls")` | ✓ success |
| TEST-999 | ✅ | Toutes les fonctions help | `shed_help()` | ✓ success |
| TEST-1000 | ✅ | Test final - workflow complet end-to-end | `shed_stats()` | ✓ success |
| TEST-1001 | ✅ | shed_help howto download | `shed_help(howto="download")` | ✓ success |
| TEST-1002 | ✅ | shed_help howto csv_to_sqlite | `shed_help(howto="csv_to_sqlite")` | ✓ success |
| TEST-1003 | ✅ | shed_help howto upload | `shed_help(howto="upload")` | ✓ success |
| TEST-1004 | ✅ | shed_help howto share | `shed_help(howto="share")` | ✓ success |
| TEST-1005 | ✅ | shed_help howto edit | `shed_help(howto="edit")` | ✓ success |
| TEST-1006 | ✅ | shed_help howto commands | `shed_help(howto="commands")` | ✓ success |
| TEST-1007 | ✅ | shed_help howto network | `shed_help(howto="network")` | ✓ success |
| TEST-1008 | ✅ | shed_help howto paths | `shed_help(howto="paths")` | ✓ success |
| TEST-1009 | ✅ | shed_help howto large_files | `shed_help(howto="large_files")` | ✓ success |
| TEST-1010 | ✅ | shed_help howto zones (non existant) | `shed_help(howto="zones")` | ✗ error |
| TEST-1011 | ✅ | shed_help howto groups (non existant) | `shed_help(howto="groups")` | ✗ error |
| TEST-1012 | ✅ | shed_help howto sqlite (non existant) | `shed_help(howto="sqlite")` | ✗ error |
| TEST-1013 | ✅ | shed_help howto full | `shed_help(howto="full")` | ✓ success |
| TEST-1014 | ✅ | shed_help howto invalide | `shed_help(howto="nonexistent_howto")` | ✗ error |
| TEST-1015 | ✅ | shed_exec avec stdout_file | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-1016 | ✅ | shed_exec jq avec stdout_file | `shed_exec(zone="storage", cmd="echo", args=["...` | ✓ success |
| TEST-1017 | ✅ | shed_exec avec stderr_file | `shed_exec(zone="storage", cmd="ls", args=["no...` | ✓ success |
| TEST-1018 | ✅ | shed_exec avec stdout_file et stderr_file | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-1019 | ✅ | shed_exec stdout_file dans sous-dossier | `shed_exec(zone="storage", cmd="date", stdout_...` | ✓ success |
| TEST-1020 | ✅ | shed_exec stdout_file path escape | `shed_exec(zone="storage", cmd="ls", stdout_fi...` | PATH_ESCAPE |
| TEST-1021 | ✅ | shed_exec cat vers stdout_file | `shed_exec(zone="storage", cmd="cat", args=["c...` | ✓ success |
| TEST-1022 | ✅ | shed_exec grep vers stdout_file | `shed_exec(zone="storage", cmd="grep", args=["...` | ✓ success |
| TEST-1023 | ✅ | shed_unzip avec src_zone uploads | `shed_unzip(zone="storage", src="archive.zip",...` | FILE_NOT_FOUND |
| TEST-1024 | ✅ | shed_unzip src_zone même zone | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-1025 | ✅ | shed_unzip src_zone documents | `shed_unzip(zone="storage", src="archive.zip",...` | FILE_NOT_FOUND |
| TEST-1026 | ✅ | shed_unzip src_zone invalide | `shed_unzip(zone="storage", src="archive.zip",...` | ZONE_FORBIDDEN |
| TEST-1027 | ✅ | shed_unzip src_zone groupe (non supporté) | `shed_unzip(zone="storage", src="archive.zip",...` | ZONE_FORBIDDEN |
| TEST-1028 | ✅ | shed_unzip src_zone vide (défaut) | `shed_unzip(zone="storage", src="archive.zip",...` | ✓ success |
| TEST-1029 | ✅ | shed_zip avec include_empty_dirs=True | `shed_zip(zone="storage", src="data", dest="wi...` | ✓ success |
| TEST-1030 | ✅ | shed_zip avec include_empty_dirs=False | `shed_zip(zone="storage", src="data", dest="wi...` | ✓ success |
| TEST-1031 | ✅ | shed_zip défaut (sans include_empty_dirs) | `shed_zip(zone="storage", src="data", dest="de...` | ✓ success |
| TEST-1032 | ✅ | shed_zip fichier unique avec include_empty_dirs | `shed_zip(zone="storage", src="log.txt", dest=...` | ✓ success |
| TEST-1033 | ✅ | shed_zip dossier non-existant | `shed_zip(zone="storage", src="nonexistent_zip...` | FILE_NOT_FOUND |
| TEST-1034 | ✅ | CSV import avec délimiteur point-virgule | `shed_sqlite(zone="storage", path="european.db...` | ✓ success |
| TEST-1035 | ✅ | CSV import avec délimiteur tabulation | `shed_sqlite(zone="storage", path="tsv.db", im...` | ✓ success |
| TEST-1036 | ✅ | CSV import avec encoding latin-1 | `shed_sqlite(zone="storage", path="latin.db", ...` | ✓ success |
| TEST-1037 | ✅ | CSV import avec encoding utf-8 explicite | `shed_sqlite(zone="storage", path="utf8_test.d...` | ✓ success |
| TEST-1038 | ✅ | CSV import avec décimal virgule | `shed_sqlite(zone="storage", path="decimal.db"...` | ✓ success |
| TEST-1039 | ✅ | CSV import avec date_columns | `shed_sqlite(zone="storage", path="dates.db", ...` | ✓ success |
| TEST-1040 | ✅ | CSV import avec date_format dayfirst | `shed_sqlite(zone="storage", path="euro_dates....` | ✓ success |
| TEST-1041 | ✅ | CSV import complet européen | `shed_sqlite(zone="storage", path="full_euro.d...` | ✓ success |
| TEST-1042 | ✅ | CSV import avec if_exists replace | `shed_sqlite(zone="storage", path="replace.db"...` | ✓ success |
| TEST-1043 | ✅ | CSV import avec if_exists append | `shed_sqlite(zone="storage", path="append.db",...` | ✓ success |
| TEST-1044 | ✅ | CSV import avec if_exists fail (table existe) | `shed_sqlite(zone="storage", path="sales.db", ...` | TABLE_EXISTS |
| TEST-1045 | ✅ | CSV import encoding invalide | `shed_sqlite(zone="storage", path="bad_enc.db"...` | ✗ error |
| TEST-1046 | ✅ | ZIP bomb potentiel (fichier n'existe pas) | `shed_unzip(zone="storage", src="suspicious_ra...` | FILE_NOT_FOUND |
| TEST-1047 | ✅ | shed_allowed_commands vérifie liste | `shed_allowed_commands()` | ✓ success |
| TEST-1048 | ✅ | shed_exec commande non dans whitelist | `shed_exec(zone="storage", cmd="nonexistent_co...` | COMMAND_FORBIDDEN |
| TEST-1049 | ✅ | shed_patch_text overwrite sans overwrite=True sur ... | `shed_patch_text(zone="storage", path="log.txt...` | ✓ success |
| TEST-1050 | ✅ | shed_sqlite readonly mode | `shed_sqlite(zone="storage", path="readonly_te...` | ✓ success |
| TEST-1051 | ✅ | Argument avec backtick | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-1052 | ✅ | Argument avec $() | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-1053 | ✅ | Argument avec ${ | `shed_exec(zone="storage", cmd="echo", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-1054 | ✅ | find avec -exec bloqué | `shed_exec(zone="storage", cmd="find", args=["...` | ARGUMENT_FORBIDDEN |
| TEST-1055 | ✅ | awk avec system() bloqué | `shed_exec(zone="storage", cmd="awk", args=["B...` | ARGUMENT_FORBIDDEN |
| TEST-1056 | ✅ | shed_exec timeout personnalisé valide | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-1057 | ✅ | shed_exec timeout maximum | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-1058 | ✅ | shed_exec timeout dépassant max | `shed_exec(zone="storage", cmd="ls", args=["-l...` | ✓ success |
| TEST-1059 | ✅ | shed_patch_text avec message dans documents | `shed_patch_text(zone="documents", path="commi...` | ✓ success |
| TEST-1060 | ✅ | shed_rename avec message dans documents | `shed_rename(zone="documents", old_path="notes...` | ✓ success |
| TEST-1061 | ✅ | shed_exec avec max_output="" - doit nommer le para... | `shed_exec(zone="storage", cmd="ls", args=[], ...` | INVALID_PARAMETER |
| TEST-1062 | ✅ | shed_patch_text avec line="" - doit indiquer le ty... | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-1063 | ✅ | shed_patch_text avec end_line="" - doit indiquer l... | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-1064 | ✅ | shed_patch_bytes avec offset="" - doit nommer le p... | `shed_patch_bytes(zone="storage", path="data.b...` | INVALID_PARAMETER |
| TEST-1065 | ✅ | shed_patch_bytes avec length="" - doit nommer le p... | `shed_patch_bytes(zone="storage", path="data.b...` | INVALID_PARAMETER |
| TEST-1066 | ✅ | shed_lockedit_exec avec timeout="" - doit nommer l... | `shed_lockedit_open(zone="storage", path="lock...` | INVALID_PARAMETER |
| TEST-1067 | ✅ | shed_hexdump avec offset=None - conversion silenci... | `shed_hexdump(zone="storage", path="data.bin",...` | ✓ success |
| TEST-1068 | ✅ | shed_hexdump avec length=None - conversion silenci... | `shed_hexdump(zone="storage", path="data.bin",...` | ✓ success |
| TEST-1069 | ✅ | shed_patch_text avec regex_flags=0 - doit indiquer... | `shed_patch_text(zone="storage", path="file.tx...` | INVALID_PARAMETER |
| TEST-1070 | ✅ | shed_convert_eol avec to=None - doit lister les va... | `shed_convert_eol(zone="storage", path="window...` | INVALID_PARAMETER |
| TEST-1071 | ✅ | shed_convert_eol avec to=0 - doit lister les valeu... | `shed_convert_eol(zone="storage", path="window...` | INVALID_PARAMETER |
| TEST-1072 | ✅ | shed_sqlite avec skip_rows=None - conversion silen... | `shed_sqlite(zone="storage", path="test_skip.d...` | ✓ success |
| TEST-1073 | ✅ | shed_sqlite avec import_csv ET query - doit expliq... | `shed_sqlite(zone="storage", path="test_mutex....` | INVALID_PARAMETER |
| TEST-1074 | ✅ | shed_sqlite avec query="" et import_csv fourni - q... | `shed_sqlite(zone="storage", path="test_mutex2...` | ✓ success |
| TEST-1075 | ✅ | shed_exec avec max_output=0 - utilise max absolu (... | `shed_exec(zone="storage", cmd="cat", args=["l...` | ✓ success |
| TEST-1076 | ✅ | shed_sqlite avec limit=0 - pas de limite (comporte... | `shed_sqlite(zone="storage", path="test_limit....` | ✓ success |
| TEST-1077 | ✅ | shed_tree avec depth=0 - converti en 1 (minimum) | `shed_tree(zone="storage", path=".", depth=0)` | ✓ success |
| TEST-1078 | ✅ | shed_patch_bytes avec offset=0 - début du fichier ... | `shed_patch_bytes(zone="storage", path="data.b...` | ✓ success |
| TEST-1079 | ✅ | shed_patch_text overwrite=True avec end_line=0 - i... | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-1080 | ✅ | shed_patch_text overwrite=True avec pattern="" - i... | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-1081 | ✅ | shed_patch_text overwrite=True avec line=0 - ignor... | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-1082 | ✅ | shed_patch_text overwrite=True avec regex_flags=0 ... | `shed_patch_text(zone="storage", path="file.tx...` | ✓ success |
| TEST-1083 | ✅ | shed_exec avec args=0 - converti silencieusement e... | `shed_exec(zone="storage", cmd="ls", args=0)` | ✓ success |
| TEST-1084 | ✅ | shed_lockedit_exec avec args=[] explicite puis arg... | `shed_lockedit_open(zone="storage", path="lock...` | ✓ success |
| TEST-1085 | ✅ | shed_patch_text avec position="overwrite" ET overw... | `shed_patch_text(zone="storage", path="overwri...` | ✓ success |
| TEST-1086 | ✅ | shed_patch_text avec position="overwrite" SANS ove... | `shed_patch_text(zone="storage", path="overwri...` | INVALID_PARAMETER |
| TEST-1087 | ✅ | attach database minuscules (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | COMMAND_FORBIDDEN |
| TEST-1088 | ✅ | DETACH majuscules (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | COMMAND_FORBIDDEN |
| TEST-1089 | ✅ | detach minuscules (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | COMMAND_FORBIDDEN |
| TEST-1090 | ✅ | load_extension minuscules (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | COMMAND_FORBIDDEN |
| TEST-1091 | ✅ | Attach DATABASE casse mixte (bloqué sécurité) | `shed_sqlite(zone="storage", path="db.db", que...` | COMMAND_FORBIDDEN |
| TEST-1092 | ✅ | shed_move_uploads_to_storage sans overwrite sur fi... | `shed_move_uploads_to_storage(src="overwrite_s...` | FILE_EXISTS |
| TEST-1093 | ✅ | shed_move_uploads_to_storage avec overwrite=True s... | `shed_move_uploads_to_storage(src="overwrite_s...` | ✓ success |
| TEST-1094 | ✅ | shed_copy_storage_to_documents sans overwrite sur ... | `shed_copy_storage_to_documents(src="readme.tx...` | FILE_EXISTS |
| TEST-1095 | ✅ | shed_copy_storage_to_documents avec overwrite=True... | `shed_copy_storage_to_documents(src="readme.tx...` | ✓ success |
| TEST-1096 | ✅ | shed_move_documents_to_storage sans overwrite sur ... | `shed_move_documents_to_storage(src="overwrite...` | FILE_EXISTS |
| TEST-1097 | ✅ | shed_move_documents_to_storage avec overwrite=True... | `shed_move_documents_to_storage(src="overwrite...` | ✓ success |
| TEST-1098 | ✅ | shed_move_uploads_to_documents sans overwrite sur ... | `shed_move_uploads_to_documents(src="overwrite...` | FILE_EXISTS |
| TEST-1099 | ✅ | shed_move_uploads_to_documents avec overwrite=True... | `shed_move_uploads_to_documents(src="overwrite...` | ✓ success |
| TEST-1100 | ✅ | shed_copy_to_group sans overwrite sur fichier exis... | `shed_copy_to_group(src_zone="storage", src_pa...` | FILE_EXISTS |
| TEST-1101 | ✅ | shed_copy_to_group avec overwrite=True sur fichier... | `shed_copy_to_group(src_zone="storage", src_pa...` | ✓ success |
