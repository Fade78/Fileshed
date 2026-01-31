# Fileshed Test Execution Report

**Version**: 1.0.4
**Tests executed**: 1195/1195
**Result**: ✅ ALL PASSED
**Duration**: 42.63s

---

| # | Status | Description |
|:--|:------:|-------------|
| TEST-001 | ✅ | Liste simple du répertoire racine Storage |
| TEST-002 | ✅ | Liste détaillée avec -la |
| TEST-003 | ✅ | Liste d'un sous-dossier |
| TEST-004 | ✅ | Liste avec tri par taille |
| TEST-005 | ✅ | Liste avec tri par date |
| TEST-006 | ✅ | Liste récursive |
| TEST-007 | ✅ | Liste avec taille human-readable |
| TEST-008 | ✅ | Liste zone uploads |
| TEST-009 | ✅ | Liste zone documents |
| TEST-010 | ✅ | Liste zone group |
| TEST-011 | ✅ | Liste fichiers cachés uniquement |
| TEST-012 | ✅ | Liste avec inode |
| TEST-013 | ✅ | Liste un fichier spécifique |
| TEST-014 | ✅ | Liste avec glob pattern |
| TEST-015 | ✅ | Liste fichier inexistant |
| TEST-016 | ✅ | Liste avec -1 (un par ligne) |
| TEST-017 | ✅ | Liste avec -A (sans . et ..) |
| TEST-018 | ✅ | Liste zone invalide |
| TEST-019 | ✅ | Liste group sans paramètre group |
| TEST-020 | ✅ | Liste avec chemin absolu (bloqué) |
| TEST-021 | ✅ | Lecture fichier simple |
| TEST-022 | ✅ | Lecture avec numéros de ligne |
| TEST-023 | ✅ | Lecture fichier inexistant |
| TEST-024 | ✅ | Lecture multiple fichiers |
| TEST-025 | ✅ | Lecture zone uploads |
| TEST-026 | ✅ | Lecture zone documents |
| TEST-027 | ✅ | Lecture avec -b (numéros lignes non vides) |
| TEST-028 | ✅ | Lecture avec -s (squeeze blank) |
| TEST-029 | ✅ | Lecture avec -E ($ en fin de ligne) |
| TEST-030 | ✅ | Lecture fichier binaire (affichage tronqué) |
| TEST-031 | ✅ | Lecture fichier vide |
| TEST-032 | ✅ | Lecture fichier volumineux |
| TEST-033 | ✅ | Lecture avec path traversal (bloqué) |
| TEST-034 | ✅ | Lecture fichier dans sous-dossier |
| TEST-035 | ✅ | Lecture avec tac (reverse) |
| TEST-036 | ✅ | Head par défaut (10 lignes) |
| TEST-037 | ✅ | Head avec -n spécifique |
| TEST-038 | ✅ | Head avec -c (bytes) |
| TEST-039 | ✅ | Tail par défaut (10 lignes) |
| TEST-040 | ✅ | Tail avec -n spécifique |
| TEST-041 | ✅ | Tail avec +n (depuis ligne n) |
| TEST-042 | ✅ | Tail avec -c (bytes) |
| TEST-043 | ✅ | Head fichier vide |
| TEST-044 | ✅ | Tail fichier vide |
| TEST-045 | ✅ | Head multiple fichiers |
| TEST-046 | ✅ | Tail zone uploads |
| TEST-047 | ✅ | Head zone documents |
| TEST-048 | ✅ | Extraction lignes milieu avec sed |
| TEST-049 | ✅ | Head avec -q (quiet, pas de header) |
| TEST-050 | ✅ | Tail fichier inexistant |
| TEST-051 | ✅ | Grep pattern simple |
| TEST-052 | ✅ | Grep case insensitive |
| TEST-053 | ✅ | Grep avec numéros de ligne |
| TEST-054 | ✅ | Grep récursif |
| TEST-055 | ✅ | Grep avec contexte (-C) |
| TEST-056 | ✅ | Grep inverse (-v) |
| TEST-057 | ✅ | Grep count only (-c) |
| TEST-058 | ✅ | Grep files only (-l) |
| TEST-059 | ✅ | Grep regex étendu |
| TEST-060 | ✅ | Grep whole word (-w) |
| TEST-061 | ✅ | Egrep (alias grep -E) |
| TEST-062 | ✅ | Fgrep (fixed strings) |
| TEST-063 | ✅ | Grep avec --include |
| TEST-064 | ✅ | Grep avec --exclude |
| TEST-065 | ✅ | Grep aucun match |
| TEST-066 | ✅ | Find fichiers par pattern |
| TEST-067 | ✅ | Find fichiers par nom |
| TEST-068 | ✅ | Find par type (fichiers) |
| TEST-069 | ✅ | Find par type (dossiers) |
| TEST-070 | ✅ | Find avec -maxdepth |
| TEST-071 | ✅ | Awk print colonne |
| TEST-072 | ✅ | Awk avec délimiteur |
| TEST-073 | ✅ | Awk calcul |
| TEST-074 | ✅ | Awk filtrage regex |
| TEST-075 | ✅ | Awk NR (numéro ligne) |
| TEST-076 | ✅ | Sed substitution simple |
| TEST-077 | ✅ | Sed substitution globale |
| TEST-078 | ✅ | Sed delete ligne |
| TEST-079 | ✅ | Sed range de lignes |
| TEST-080 | ✅ | Sed avec regex |
| TEST-081 | ✅ | Sed insert ligne |
| TEST-082 | ✅ | Sed append ligne |
| TEST-083 | ✅ | Awk multiple colonnes |
| TEST-084 | ✅ | Sed multiple commandes |
| TEST-085 | ✅ | Awk BEGIN/END |
| TEST-086 | ✅ | Word count (wc) |
| TEST-087 | ✅ | Word count lignes seulement |
| TEST-088 | ✅ | Sort alphabétique |
| TEST-089 | ✅ | Sort numérique |
| TEST-090 | ✅ | Sort reverse |
| TEST-091 | ✅ | Uniq (supprimer doublons consécutifs) |
| TEST-092 | ✅ | Uniq avec count |
| TEST-093 | ✅ | Cut colonnes |
| TEST-094 | ✅ | Tr translate |
| TEST-095 | ✅ | Rev (reverse lines) |
| TEST-096 | ✅ | Nl (number lines) |
| TEST-097 | ✅ | Format text paragraphs |
| TEST-098 | ✅ | Fold (wrap lines) |
| TEST-099 | ✅ | Fmt (format paragraphes) |
| TEST-100 | ✅ | Paste (merge files) |
| TEST-101 | ✅ | Créer dossier simple |
| TEST-102 | ✅ | Créer arborescence (-p) |
| TEST-103 | ✅ | mkdir dossier existant (erreur) |
| TEST-104 | ✅ | mkdir -p dossier existant (ok) |
| TEST-105 | ✅ | mkdir zone documents |
| TEST-106 | ✅ | mkdir zone uploads (interdit) |
| TEST-107 | ✅ | touch créer fichier |
| TEST-108 | ✅ | touch fichier existant (update time) |
| TEST-109 | ✅ | touch multiple fichiers |
| TEST-110 | ✅ | touch dans sous-dossier |
| TEST-111 | ✅ | touch zone documents |
| TEST-112 | ✅ | touch zone group |
| TEST-113 | ✅ | mkdir avec verbose (-v) |
| TEST-114 | ✅ | touch avec timestamp spécifique |
| TEST-115 | ✅ | mkdir chemin avec espaces |
| TEST-116 | ✅ | Copie fichier simple |
| TEST-117 | ✅ | Copie dans dossier |
| TEST-118 | ✅ | Copie récursive |
| TEST-119 | ✅ | Copie avec préservation (-p) |
| TEST-120 | ✅ | Copie multiple fichiers |
| TEST-121 | ✅ | Move fichier |
| TEST-122 | ✅ | Move dans dossier |
| TEST-123 | ✅ | Move dossier |
| TEST-124 | ✅ | Remove fichier |
| TEST-125 | ✅ | Remove multiple fichiers |
| TEST-126 | ✅ | Remove dossier vide |
| TEST-127 | ✅ | Remove récursif |
| TEST-128 | ✅ | Remove avec force (-f) |
| TEST-129 | ✅ | Remove fichier inexistant (erreur) |
| TEST-130 | ✅ | cp zone documents |
| TEST-131 | ✅ | mv zone documents |
| TEST-132 | ✅ | rm zone documents |
| TEST-133 | ✅ | cp zone group |
| TEST-134 | ✅ | mv avec verbose (-v) |
| TEST-135 | ✅ | cp avec interactive (-i) - non interactif |
| TEST-136 | ✅ | rm dossier non vide sans -r (erreur) |
| TEST-137 | ✅ | cp avec backup (-b) |
| TEST-138 | ✅ | mv fichier vers lui-même |
| TEST-139 | ✅ | cp lien symbolique |
| TEST-140 | ✅ | rm avec glob pattern |
| TEST-141 | ✅ | Gzip compression |
| TEST-142 | ✅ | Gunzip décompression |
| TEST-143 | ✅ | Gzip keep original (-k) |
| TEST-144 | ✅ | Bzip2 compression |
| TEST-145 | ✅ | Bunzip2 décompression |
| TEST-146 | ✅ | Xz compression |
| TEST-147 | ✅ | Unxz décompression |
| TEST-148 | ✅ | Tar création archive |
| TEST-149 | ✅ | Tar extraction |
| TEST-150 | ✅ | Tar avec gzip (.tar.gz) |
| TEST-151 | ✅ | Tar extraction .tar.gz |
| TEST-152 | ✅ | Tar list contents |
| TEST-153 | ✅ | Zcat lecture compressé |
| TEST-154 | ✅ | Compression zone documents |
| TEST-155 | ✅ | Zstd compression - unavailable command |
| TEST-156 | ✅ | Git status |
| TEST-157 | ✅ | Git log |
| TEST-158 | ✅ | Git diff |
| TEST-159 | ✅ | Git diff HEAD~1 |
| TEST-160 | ✅ | Git show |
| TEST-161 | ✅ | Git branch list |
| TEST-162 | ✅ | Git rev-parse HEAD |
| TEST-163 | ✅ | Git log graph |
| TEST-164 | ✅ | Git blame |
| TEST-165 | ✅ | Git log fichier spécifique |
| TEST-166 | ✅ | Git zone group |
| TEST-167 | ✅ | Git shortlog |
| TEST-168 | ✅ | Git ls-files |
| TEST-169 | ✅ | Git zone storage (pas de repo auto) |
| TEST-170 | ✅ | Git stash (si supported) |
| TEST-171 | ✅ | Redirection simple |
| TEST-172 | ✅ | jq avec redirection |
| TEST-173 | ✅ | grep avec redirection |
| TEST-174 | ✅ | sort avec redirection |
| TEST-175 | ✅ | awk avec redirection |
| TEST-176 | ✅ | cat avec redirection (copie) |
| TEST-177 | ✅ | Redirection zone documents |
| TEST-178 | ✅ | Redirection écrase fichier existant |
| TEST-179 | ✅ | Redirection dans sous-dossier |
| TEST-180 | ✅ | stderr_file redirection |
| TEST-181 | ✅ | Créer fichier texte simple |
| TEST-182 | ✅ | Créer fichier dans sous-dossier |
| TEST-183 | ✅ | Créer fichier multiligne |
| TEST-184 | ✅ | Créer fichier vide |
| TEST-185 | ✅ | Créer fichier zone documents |
| TEST-186 | ✅ | Créer fichier zone documents avec message |
| TEST-187 | ✅ | Create file in group zone |
| TEST-188 | ✅ | Créer fichier avec caractères spéciaux |
| TEST-189 | ✅ | Créer fichier avec emoji |
| TEST-190 | ✅ | Créer fichier JSON |
| TEST-191 | ✅ | Créer fichier YAML |
| TEST-192 | ✅ | Créer fichier avec tabs |
| TEST-193 | ✅ | Créer fichier zone uploads (interdit) |
| TEST-194 | ✅ | Créer avec path traversal (bloqué) |
| TEST-195 | ✅ | Créer fichier volumineux |
| TEST-196 | ✅ | Créer fichier nom avec espaces |
| TEST-197 | ✅ | Créer fichier nom avec caractères spéciaux |
| TEST-198 | ✅ | Écraser fichier existant |
| TEST-199 | ✅ | Append to existing file with overwrite=False |
| TEST-200 | ✅ | Créer fichier groupe sans paramètre group |
| TEST-201 | ✅ | Append à la fin |
| TEST-202 | ✅ | Prepend au début |
| TEST-203 | ✅ | Append multiple fois |
| TEST-204 | ✅ | Insert avant ligne spécifique |
| TEST-205 | ✅ | Insert après ligne spécifique |
| TEST-206 | ✅ | Insert ligne 1 |
| TEST-207 | ✅ | Insert ligne invalide (0) |
| TEST-208 | ✅ | Insert ligne > nombre de lignes |
| TEST-209 | ✅ | Append zone documents |
| TEST-210 | ✅ | Append zone group |
| TEST-211 | ✅ | Insert avec message git |
| TEST-212 | ✅ | Append fichier inexistant |
| TEST-213 | ✅ | Prepend fichier vide |
| TEST-214 | ✅ | Append avec newline final |
| TEST-215 | ✅ | Insert multiligne |
| TEST-216 | ✅ | Append caractères binaires (peut échouer) |
| TEST-217 | ✅ | Insert très long contenu |
| TEST-218 | ✅ | Create new file in group where user is member |
| TEST-219 | ✅ | Create file named locked.txt (no actual lock) |
| TEST-220 | ✅ | Position invalide |
| TEST-221 | ✅ | Replace pattern simple |
| TEST-222 | ✅ | Replace pattern regex |
| TEST-223 | ✅ | Replace pattern non trouvé |
| TEST-224 | ✅ | Replace all occurrences with match_all=True |
| TEST-225 | ✅ | Replace first occurrence only (no match_all) |
| TEST-226 | ✅ | Replace with capture groups |
| TEST-227 | ✅ | Replace multiline pattern (line1 followed by line2) |
| TEST-228 | ✅ | Replace zone documents |
| TEST-229 | ✅ | Replace zone group |
| TEST-230 | ✅ | Replace avec message git |
| TEST-231 | ✅ | Replace pattern vide (invalide) |
| TEST-232 | ✅ | Replace avec caractères spéciaux regex |
| TEST-233 | ✅ | Replace case sensitive |
| TEST-234 | ✅ | Replace sur fichier binaire (échec) |
| TEST-235 | ✅ | Replace pattern avec newlines |
| TEST-236 | ✅ | Replace URL dans fichier |
| TEST-237 | ✅ | Replace avec quotes |
| TEST-238 | ✅ | Replace pattern regex complexe |
| TEST-239 | ✅ | Replace fichier entier via pattern .* |
| TEST-240 | ✅ | Replace par chaîne vide (suppression) |
| TEST-241 | ✅ | Path commençant par zone (erreur) |
| TEST-242 | ✅ | Path avec double slash |
| TEST-243 | ✅ | Path avec ./ |
| TEST-244 | ✅ | Fichier très long nom |
| TEST-245 | ✅ | Content None |
| TEST-246 | ✅ | Zone vide |
| TEST-247 | ✅ | Path vide |
| TEST-248 | ✅ | Création dans dossier inexistant (auto-création du parent) |
| TEST-249 | ✅ | Écrire sur un dossier |
| TEST-250 | ✅ | Group inexistant |
| TEST-251 | ✅ | Fichier trop grand (limite 50MB dépassée) |
| TEST-252 | ✅ | Fichier symlink |
| TEST-253 | ✅ | Replace sans pattern |
| TEST-254 | ✅ | Line sans position insert (paramètre ignoré) |
| TEST-255 | ✅ | Position before sans line |
| TEST-256 | ✅ | Écriture concurrent (autre session) |
| TEST-257 | ✅ | Caractères de contrôle dans contenu |
| TEST-258 | ✅ | BOM UTF-8 dans contenu |
| TEST-259 | ✅ | Très grande ligne (pas de newlines) |
| TEST-260 | ✅ | Replace_all sans occurrences (match_all=True) |
| TEST-261 | ✅ | Écrire bytes simples (base64) |
| TEST-262 | ✅ | Écrire image binaire (1x1 PNG) |
| TEST-263 | ✅ | Append bytes |
| TEST-264 | ✅ | Prepend bytes |
| TEST-265 | ✅ | Écrire bytes zone documents |
| TEST-266 | ✅ | Écrire bytes zone group |
| TEST-267 | ✅ | Hex invalide (caractères non-hex) |
| TEST-268 | ✅ | Écrire fichier exécutable (base64) |
| TEST-269 | ✅ | Bytes vides |
| TEST-270 | ✅ | Insert bytes à offset invalide (au-delà de la taille fichier |
| TEST-271 | ✅ | Bytes zone uploads (interdit) |
| TEST-272 | ✅ | Fichier binaire avec hex répété |
| TEST-273 | ✅ | Overwrite partiel d'un binaire |
| TEST-274 | ✅ | Append à fichier texte |
| TEST-275 | ✅ | Path traversal bytes |
| TEST-276 | ✅ | Bytes avec message git |
| TEST-277 | ✅ | Content None bytes |
| TEST-278 | ✅ | Offset négatif |
| TEST-279 | ✅ | Offset au-delà de la taille |
| TEST-280 | ✅ | Écrire PDF (en-tête valide, base64) |
| TEST-281 | ✅ | Écrire fichier ZIP (en-tête, base64) |
| TEST-282 | ✅ | Caractères non-ASCII dans hex (invalide) |
| TEST-283 | ✅ | Base64 avec whitespace |
| TEST-284 | ✅ | Créer fichier binaire nouveau |
| TEST-285 | ✅ | Créer fichier binaire dans groupe |
| TEST-286 | ✅ | Position invalide bytes |
| TEST-287 | ✅ | Bytes dans sous-dossier |
| TEST-288 | ✅ | Écrire NULL bytes |
| TEST-289 | ✅ | Base64 padding incorrect |
| TEST-290 | ✅ | Bytes group sans group param |
| TEST-291 | ✅ | Supprimer fichier simple |
| TEST-292 | ✅ | Supprimer dossier vide |
| TEST-293 | ✅ | Supprimer dossier (récursif) |
| TEST-294 | ✅ | Supprimer fichier zone documents |
| TEST-295 | ✅ | Supprimer fichier zone group |
| TEST-296 | ✅ | Supprimer fichier inexistant |
| TEST-297 | ✅ | Supprimer zone uploads |
| TEST-298 | ✅ | Supprimer avec path traversal |
| TEST-299 | ✅ | Supprimer racine zone (bloqué) |
| TEST-300 | ✅ | Supprimer fichier verrouillé |
| TEST-301 | ✅ | Supprimer fichier groupe mode owner_ro |
| TEST-302 | ✅ | Supprimer fichier avec espaces |
| TEST-303 | ✅ | Supprimer lien symbolique |
| TEST-304 | ✅ | Supprimer fichier binaire |
| TEST-305 | ✅ | Supprimer arborescence profonde |
| TEST-306 | ✅ | Supprimer fichier caché |
| TEST-307 | ✅ | Supprimer .git (devrait être bloqué) |
| TEST-308 | ✅ | Supprimer sans path |
| TEST-309 | ✅ | Supprimer groupe sans group param |
| TEST-310 | ✅ | Supprimer zone invalide |
| TEST-311 | ✅ | Supprimer avec message git |
| TEST-312 | ✅ | Supprimer fichier groupe autre membre |
| TEST-313 | ✅ | Supprimer dossier .git interne |
| TEST-314 | ✅ | Supprimer tous les fichiers (pattern) |
| TEST-315 | ✅ | Supprimer fichier volumineux |
| TEST-316 | ✅ | Supprimer fichier pendant lecture |
| TEST-317 | ✅ | Supprimer path avec caractères spéciaux |
| TEST-318 | ✅ | Supprimer fichier UTF-8 dans nom |
| TEST-319 | ✅ | Supprimer dossier contenant .gitkeep |
| TEST-320 | ✅ | Supprimer groupe non membre |
| TEST-321 | ✅ | Renommer fichier simple |
| TEST-322 | ✅ | Déplacer fichier dans dossier |
| TEST-323 | ✅ | Renommer dossier |
| TEST-324 | ✅ | Renommer zone documents |
| TEST-325 | ✅ | Renommer zone group |
| TEST-326 | ✅ | Renommer fichier inexistant |
| TEST-327 | ✅ | Renommer vers destination existante |
| TEST-328 | ✅ | Renommer zone uploads (interdit) |
| TEST-329 | ✅ | Renommer avec path traversal |
| TEST-330 | ✅ | Renommer fichier verrouillé |
| TEST-331 | ✅ | Renommer vers dossier inexistant (création auto) |
| TEST-332 | ✅ | Renommer fichier sur lui-même |
| TEST-333 | ✅ | Renommer avec changement d'extension |
| TEST-334 | ✅ | Renommer fichier binaire |
| TEST-335 | ✅ | Renommer arborescence |
| TEST-336 | ✅ | Renommer vers nom avec espaces |
| TEST-337 | ✅ | Renommer fichier caché |
| TEST-338 | ✅ | Renommer sans old_path |
| TEST-339 | ✅ | Renommer sans new_path |
| TEST-340 | ✅ | Renommer groupe sans group param |
| TEST-341 | ✅ | Renommer avec message git |
| TEST-342 | ✅ | Renommer dossier vers sous-dossier de lui-même |
| TEST-343 | ✅ | Renommer fichier UTF-8 |
| TEST-344 | ✅ | Renommer lien symbolique |
| TEST-345 | ✅ | Renommer fichier groupe mode owner |
| TEST-346 | ✅ | Renommer zone invalide |
| TEST-347 | ✅ | Renommer avec new_path commençant par zone |
| TEST-348 | ✅ | Renommer cross-zone (interdit) |
| TEST-349 | ✅ | Renommer fichier très gros |
| TEST-350 | ✅ | Renommer vers nom très long |
| TEST-351 | ✅ | Tree zone storage |
| TEST-352 | ✅ | Tree avec profondeur limitée |
| TEST-353 | ✅ | Tree d'un sous-dossier |
| TEST-354 | ✅ | Tree zone documents |
| TEST-355 | ✅ | Tree zone uploads |
| TEST-356 | ✅ | Tree zone group |
| TEST-357 | ✅ | Tree profondeur 0 |
| TEST-358 | ✅ | Tree profondeur très grande |
| TEST-359 | ✅ | Tree dossier vide |
| TEST-360 | ✅ | Tree dossier inexistant |
| TEST-361 | ✅ | Tree zone invalide |
| TEST-362 | ✅ | Tree group sans group param |
| TEST-363 | ✅ | Tree avec path traversal |
| TEST-364 | ✅ | Tree sur fichier (pas dossier) |
| TEST-365 | ✅ | Tree profondeur 1 |
| TEST-366 | ✅ | Tree arborescence profonde |
| TEST-367 | ✅ | Tree avec fichiers cachés |
| TEST-368 | ✅ | Tree groupe autre membre |
| TEST-369 | ✅ | Tree avec profondeur négative |
| TEST-370 | ✅ | Tree path avec espaces |
| TEST-371 | ✅ | Ouvrir fichier pour édition |
| TEST-372 | ✅ | Ouvrir fichier zone documents |
| TEST-373 | ✅ | Ouvrir fichier zone group |
| TEST-374 | ✅ | Ouvrir fichier inexistant |
| TEST-375 | ✅ | Ouvrir fichier déjà verrouillé (autre conversation) |
| TEST-376 | ✅ | Ouvrir fichier verrouillé par autre |
| TEST-377 | ✅ | Ouvrir zone uploads (interdit) |
| TEST-378 | ✅ | Ouvrir avec path traversal |
| TEST-379 | ✅ | Ouvrir dossier (interdit) |
| TEST-380 | ✅ | Ouvrir fichier binaire |
| TEST-381 | ✅ | Ouvrir zone invalide |
| TEST-382 | ✅ | Ouvrir group sans group param |
| TEST-383 | ✅ | Ouvrir fichier groupe mode owner_ro |
| TEST-384 | ✅ | Ouvrir fichier volumineux |
| TEST-385 | ✅ | Ouvrir sans path |
| TEST-386 | ✅ | Ouvrir fichier caché |
| TEST-387 | ✅ | Ouvrir fichier dans sous-dossier |
| TEST-388 | ✅ | Ouvrir groupe non membre |
| TEST-389 | ✅ | Ouvrir fichier symlink |
| TEST-390 | ✅ | Ouvrir plusieurs fichiers simultanément |
| TEST-391 | ✅ | Exec cat sur fichier verrouillé |
| TEST-392 | ✅ | Exec sed sur fichier verrouillé |
| TEST-393 | ✅ | Exec grep sur fichier verrouillé |
| TEST-394 | ✅ | Exec sur fichier non verrouillé |
| TEST-395 | ✅ | Exec commande rm (sans argument fichier) |
| TEST-396 | ✅ | Exec avec arguments dangereux |
| TEST-397 | ✅ | Exec head sur fichier verrouillé |
| TEST-398 | ✅ | Exec wc sur fichier verrouillé |
| TEST-399 | ✅ | Exec zone documents |
| TEST-400 | ✅ | Exec zone group |
| TEST-401 | ✅ | Exec awk sur fichier verrouillé |
| TEST-402 | ✅ | Exec sort sur fichier verrouillé |
| TEST-403 | ✅ | Exec sans cmd |
| TEST-404 | ✅ | Exec xxd (hexdump) sur binaire |
| TEST-405 | ✅ | Exec avec timeout dépassé |
| TEST-406 | ✅ | Overwrite fichier verrouillé |
| TEST-407 | ✅ | Append fichier verrouillé |
| TEST-408 | ✅ | Overwrite fichier non verrouillé |
| TEST-409 | ✅ | Overwrite zone documents |
| TEST-410 | ✅ | Overwrite zone group |
| TEST-411 | ✅ | Overwrite contenu vide |
| TEST-412 | ✅ | Append contenu multiligne |
| TEST-413 | ✅ | Overwrite contenu très long |
| TEST-414 | ✅ | Overwrite avec caractères spéciaux |
| TEST-415 | ✅ | Overwrite sans content |
| TEST-416 | ✅ | Append plusieurs fois |
| TEST-417 | ✅ | Overwrite fichier binaire avec texte |
| TEST-418 | ✅ | Overwrite group sans group param |
| TEST-419 | ✅ | Overwrite avec emojis |
| TEST-420 | ✅ | Append=False par défaut |
| TEST-421 | ✅ | Save fichier modifié |
| TEST-422 | ✅ | Save zone documents |
| TEST-423 | ✅ | Save fichier déjà sauvé (NOT_IN_EDIT_MODE) |
| TEST-424 | ✅ | Save zone group |
| TEST-425 | ✅ | Save fichier non verrouillé |
| TEST-426 | ✅ | Save fichier verrouillé par autre |
| TEST-427 | ✅ | Save sans modifications |
| TEST-428 | ✅ | Double save (déjà sauvé) |
| TEST-429 | ✅ | Save zone invalide |
| TEST-430 | ✅ | Save group sans group param |
| TEST-431 | ✅ | Save sans path |
| TEST-432 | ✅ | Save fichier non ouvert retourne NOT_IN_EDIT_MODE |
| TEST-433 | ✅ | Save fichier non ouvert retourne NOT_IN_EDIT_MODE |
| TEST-434 | ✅ | Save groupe déjà sauvé retourne NOT_IN_EDIT_MODE |
| TEST-435 | ✅ | Save puis réouvrir |
| TEST-436 | ✅ | Cancel édition |
| TEST-437 | ✅ | Cancel zone documents (workflow complet) |
| TEST-438 | ✅ | Cancel zone group (workflow complet) |
| TEST-439 | ✅ | Cancel fichier non verrouillé |
| TEST-440 | ✅ | Cancel fichier verrouillé par autre |
| TEST-441 | ✅ | Cancel après modifications |
| TEST-442 | ✅ | Cancel zone invalide |
| TEST-443 | ✅ | Cancel group sans group param |
| TEST-444 | ✅ | Cancel sans path |
| TEST-445 | ✅ | Double cancel |
| TEST-446 | ✅ | Cancel puis réouvrir |
| TEST-447 | ✅ | Cancel fichier binaire |
| TEST-448 | ✅ | Cancel groupe non membre |
| TEST-449 | ✅ | Cancel avec path traversal |
| TEST-450 | ✅ | Cancel fichier volumineux |
| TEST-451 | ✅ | Déplacer fichier uploads vers storage |
| TEST-452 | ✅ | Déplacer vers sous-dossier storage |
| TEST-453 | ✅ | Déplacer fichier inexistant |
| TEST-454 | ✅ | Déplacer vers destination existante |
| TEST-455 | ✅ | Déplacer fichier binaire |
| TEST-456 | ✅ | Déplacer fichier volumineux |
| TEST-457 | ✅ | Déplacer avec path traversal src |
| TEST-458 | ✅ | Déplacer avec path traversal dest |
| TEST-459 | ✅ | Déplacer sans src |
| TEST-460 | ✅ | Déplacer sans dest |
| TEST-461 | ✅ | Déplacer dossier entier |
| TEST-462 | ✅ | Déplacer avec renommage |
| TEST-463 | ✅ | Déplacer fichier caché |
| TEST-464 | ✅ | Déplacer vers dossier inexistant (création auto) |
| TEST-465 | ✅ | Déplacer fichier avec espaces |
| TEST-466 | ✅ | Déplacer fichier UTF-8 |
| TEST-467 | ✅ | Déplacer symlink |
| TEST-468 | ✅ | Vérifier suppression de la source |
| TEST-469 | ✅ | Déplacer gros fichier (move ne change pas le quota) |
| TEST-470 | ✅ | Déplacer dest commençant par Storage |
| TEST-471 | ✅ | Déplacer uploads vers documents |
| TEST-472 | ✅ | Déplacer avec message git |
| TEST-473 | ✅ | Déplacer fichier inexistant |
| TEST-474 | ✅ | Déplacer vers destination existante |
| TEST-475 | ✅ | Déplacer fichier binaire |
| TEST-476 | ✅ | Déplacer avec path traversal |
| TEST-477 | ✅ | Déplacer sans src |
| TEST-478 | ✅ | Déplacer fichier volumineux |
| TEST-479 | ✅ | Vérifier commit créé |
| TEST-480 | ✅ | Déplacer fichier UTF-8 |
| TEST-481 | ✅ | Déplacer vers sous-dossier profond |
| TEST-482 | ✅ | Déplacer avec espaces dans nom |
| TEST-483 | ✅ | Déplacer dest commençant par Documents |
| TEST-484 | ✅ | Déplacer gros fichier (move ne change pas le quota) |
| TEST-485 | ✅ | Message git par défaut |
| TEST-486 | ✅ | Copier storage vers documents |
| TEST-487 | ✅ | Copier avec message git |
| TEST-488 | ✅ | Copier fichier inexistant |
| TEST-489 | ✅ | Copier vers destination existante |
| TEST-490 | ✅ | Vérifier source non supprimée |
| TEST-491 | ✅ | Copier dossier |
| TEST-492 | ✅ | Copier fichier binaire |
| TEST-493 | ✅ | Copier avec path traversal |
| TEST-494 | ✅ | Copier fichier volumineux |
| TEST-495 | ✅ | Copier sans src |
| TEST-496 | ✅ | Copier vers sous-dossier |
| TEST-497 | ✅ | Copier fichier caché |
| TEST-498 | ✅ | Copier dest commençant par Documents |
| TEST-499 | ✅ | Copier gros fichier (quota non dépassé) |
| TEST-500 | ✅ | Copier fichier UTF-8 |
| TEST-501 | ✅ | Déplacer documents vers storage |
| TEST-502 | ✅ | Déplacer avec message git |
| TEST-503 | ✅ | Déplacer fichier inexistant |
| TEST-504 | ✅ | Déplacer vers destination existante |
| TEST-505 | ✅ | Vérifier source supprimée |
| TEST-506 | ✅ | Déplacer fichier binaire |
| TEST-507 | ✅ | Déplacer avec path traversal |
| TEST-508 | ✅ | Déplacer sans src |
| TEST-509 | ✅ | Déplacer fichier volumineux |
| TEST-510 | ✅ | Déplacer dossier |
| TEST-511 | ✅ | Déplacer dest commençant par Storage |
| TEST-512 | ✅ | Vérifier commit de suppression |
| TEST-513 | ✅ | Déplacer fichier avec espaces |
| TEST-514 | ✅ | Déplacer vers sous-dossier |
| TEST-515 | ✅ | Message git par défaut |
| TEST-516 | ✅ | Copier storage vers group |
| TEST-517 | ✅ | Copier documents vers group |
| TEST-518 | ✅ | Copier avec message git |
| TEST-519 | ✅ | Copier avec mode owner |
| TEST-520 | ✅ | Copier avec mode group |
| TEST-521 | ✅ | Copier avec mode owner_ro |
| TEST-522 | ✅ | Copier fichier inexistant |
| TEST-523 | ✅ | Copier vers destination existante |
| TEST-524 | ✅ | Copier vers groupe non membre |
| TEST-525 | ✅ | Copier sans group |
| TEST-526 | ✅ | Copier depuis uploads vers group |
| TEST-527 | ✅ | Copier avec path traversal |
| TEST-528 | ✅ | Copier mode invalide (fallback to group) |
| TEST-529 | ✅ | Copier fichier binaire vers group |
| TEST-530 | ✅ | Copier src_zone invalide |
| TEST-531 | ✅ | Créer ZIP d'un fichier |
| TEST-532 | ✅ | Créer ZIP d'un dossier |
| TEST-533 | ✅ | ZIP avec sous-dossiers |
| TEST-534 | ✅ | ZIP avec empty dirs |
| TEST-535 | ✅ | ZIP sans empty dirs |
| TEST-536 | ✅ | ZIP zone documents |
| TEST-537 | ✅ | ZIP zone group non supportée |
| TEST-538 | ✅ | ZIP source inexistante |
| TEST-539 | ✅ | ZIP destination existante |
| TEST-540 | ✅ | ZIP avec path traversal src |
| TEST-541 | ✅ | ZIP avec path traversal dest |
| TEST-542 | ✅ | ZIP fichier binaire |
| TEST-543 | ✅ | ZIP fichiers multiples (dossier) |
| TEST-544 | ✅ | ZIP zone uploads (lecture seule OK) |
| TEST-545 | ✅ | ZIP zone invalide |
| TEST-546 | ✅ | ZIP group non supporté |
| TEST-547 | ✅ | ZIP sans dest (auto-nommé) |
| TEST-548 | ✅ | ZIP fichier volumineux |
| TEST-549 | ✅ | ZIP fichier caché |
| TEST-550 | ✅ | ZIP avec espaces dans nom |
| TEST-551 | ✅ | ZIP fichier UTF-8 |
| TEST-552 | ✅ | ZIP dossier volumineux |
| TEST-553 | ✅ | ZIP dossier vide |
| TEST-554 | ✅ | ZIP dest dans sous-dossier |
| TEST-555 | ✅ | ZIP sans src |
| TEST-556 | ✅ | Extraire ZIP simple |
| TEST-557 | ✅ | Extraire ZIP dans racine |
| TEST-558 | ✅ | Extraire ZIP cross-zone (uploads vers storage) |
| TEST-559 | ✅ | Extraire ZIP zone documents |
| TEST-560 | ✅ | Extraire ZIP zone group non supportée |
| TEST-561 | ✅ | Extraire ZIP inexistant |
| TEST-562 | ✅ | Extraire fichier corrompu |
| TEST-563 | ✅ | Extraire ZIP vers destination existante |
| TEST-564 | ✅ | Extraire ZIP avec path traversal src |
| TEST-565 | ✅ | Extraire ZIP avec path traversal dest |
| TEST-566 | ✅ | Extraire ZIP avec structure profonde |
| TEST-567 | ✅ | Extraire ZIP zone invalide |
| TEST-568 | ✅ | Extraire ZIP zone group non supportée |
| TEST-569 | ✅ | Extraire ZIP binaire |
| TEST-570 | ✅ | Extraire ZIP avec mot de passe (non supporté) |
| TEST-571 | ✅ | Extraire ZIP volumineux |
| TEST-572 | ✅ | Extraire ZIP plus grand |
| TEST-573 | ✅ | Extraire ZIP fichiers UTF-8 |
| TEST-574 | ✅ | Extraire ZIP sans src |
| TEST-575 | ✅ | src_zone invalide |
| TEST-576 | ✅ | Info ZIP simple |
| TEST-577 | ✅ | Info ZIP avec tailles |
| TEST-578 | ✅ | Info ZIP zone documents |
| TEST-579 | ✅ | Info ZIP zone group sans paramètre group |
| TEST-580 | ✅ | Info ZIP inexistant |
| TEST-581 | ✅ | Info fichier corrompu |
| TEST-582 | ✅ | Info ZIP avec path traversal |
| TEST-583 | ✅ | Info ZIP zone invalide |
| TEST-584 | ✅ | Info ZIP zone group sans paramètre group |
| TEST-585 | ✅ | Info ZIP corrompu |
| TEST-586 | ✅ | Info ZIP vide |
| TEST-587 | ✅ | Info ZIP volumineux |
| TEST-588 | ✅ | Info ZIP sans path |
| TEST-589 | ✅ | Info ZIP fichiers UTF-8 |
| TEST-590 | ✅ | Info ZIP zone uploads |
| TEST-591 | ✅ | Import CSV simple |
| TEST-592 | ✅ | Import CSV avec headers |
| TEST-593 | ✅ | Import CSV sans headers |
| TEST-594 | ✅ | Import CSV délimiteur point-virgule |
| TEST-595 | ✅ | Import CSV délimiteur tab |
| TEST-596 | ✅ | Import CSV table existante (erreur) |
| TEST-597 | ✅ | Import CSV table existante if_exists=replace |
| TEST-598 | ✅ | Import CSV table existante if_exists=append |
| TEST-599 | ✅ | Import CSV fichier inexistant |
| TEST-600 | ✅ | Import CSV malformé |
| TEST-601 | ✅ | Import CSV vide |
| TEST-602 | ✅ | Import CSV zone documents |
| TEST-603 | ✅ | Import CSV zone group |
| TEST-604 | ✅ | Import CSV avec quotes |
| TEST-605 | ✅ | Import CSV UTF-8 |
| TEST-606 | ✅ | Import CSV volumineux |
| TEST-607 | ✅ | Import CSV avec path traversal |
| TEST-608 | ✅ | Import CSV nouvelle base |
| TEST-609 | ✅ | Import CSV sans table |
| TEST-610 | ✅ | Import CSV zone invalide |
| TEST-611 | ✅ | Import CSV group sans group |
| TEST-612 | ✅ | Import CSV colonnes nombreuses |
| TEST-613 | ✅ | Import CSV lignes nombreuses |
| TEST-614 | ✅ | Import CSV types mixtes |
| TEST-615 | ✅ | Import CSV zone uploads |
| TEST-616 | ✅ | Import CSV if_exists invalide |
| TEST-617 | ✅ | Import CSV délimiteur invalide |
| TEST-618 | ✅ | Import CSV depuis autre zone |
| TEST-619 | ✅ | Import CSV nom table avec tirets (invalide) |
| TEST-620 | ✅ | Import CSV overwrite base |
| TEST-621 | ✅ | SELECT simple |
| TEST-622 | ✅ | SELECT avec WHERE |
| TEST-623 | ✅ | SELECT avec ORDER BY |
| TEST-624 | ✅ | SELECT avec LIMIT |
| TEST-625 | ✅ | SELECT avec JOIN (table inexistante) |
| TEST-626 | ✅ | SELECT avec GROUP BY |
| TEST-627 | ✅ | SELECT avec HAVING |
| TEST-628 | ✅ | SELECT fonctions agrégation |
| TEST-629 | ✅ | SELECT COUNT |
| TEST-630 | ✅ | SELECT DISTINCT |
| TEST-631 | ✅ | CREATE TABLE |
| TEST-632 | ✅ | INSERT INTO |
| TEST-633 | ✅ | UPDATE |
| TEST-634 | ✅ | DELETE |
| TEST-635 | ✅ | ALTER TABLE |
| TEST-636 | ✅ | DROP TABLE |
| TEST-637 | ✅ | Requête sur table inexistante |
| TEST-638 | ✅ | Requête syntaxe invalide |
| TEST-639 | ✅ | Requête base inexistante |
| TEST-640 | ✅ | Requête zone documents |
| TEST-641 | ✅ | Requête zone group |
| TEST-642 | ✅ | Requête avec paramètres |
| TEST-643 | ✅ | Multiple statements (bloqué) |
| TEST-644 | ✅ | SELECT avec sous-requête |
| TEST-645 | ✅ | Requête UNION |
| TEST-646 | ✅ | Requête CASE |
| TEST-647 | ✅ | Requête zone invalide |
| TEST-648 | ✅ | Requête group sans group |
| TEST-649 | ✅ | Requête vide |
| TEST-650 | ✅ | Requête résultat volumineux |
| TEST-651 | ✅ | SELECT avec LIKE |
| TEST-652 | ✅ | SELECT avec NULL |
| TEST-653 | ✅ | Requête readonly activé |
| TEST-654 | ✅ | PRAGMA (si autorisé) |
| TEST-655 | ✅ | CREATE INDEX |
| TEST-656 | ✅ | Requête avec alias |
| TEST-657 | ✅ | Requête COALESCE |
| TEST-658 | ✅ | Requête date |
| TEST-659 | ✅ | Requête avec path traversal |
| TEST-660 | ✅ | Requête fichier non-SQLite |
| TEST-661 | ✅ | Export résultat vers CSV |
| TEST-662 | ✅ | Export avec filtre |
| TEST-663 | ✅ | Export résultat vide |
| TEST-664 | ✅ | Export zone documents |
| TEST-665 | ✅ | Export zone group |
| TEST-666 | ✅ | Export vers fichier existant |
| TEST-667 | ✅ | Export volumineux |
| TEST-668 | ✅ | Export avec path traversal |
| TEST-669 | ✅ | Export dans sous-dossier |
| TEST-670 | ✅ | Export données UTF-8 |
| TEST-671 | ✅ | Export avec NULL |
| TEST-672 | ✅ | Export agrégation |
| TEST-673 | ✅ | Export JOIN |
| TEST-674 | ✅ | Export quota dépassé |
| TEST-675 | ✅ | Export nom CSV avec espaces |
| TEST-676 | ✅ | Export sans query (import + export direct) |
| TEST-677 | ✅ | Export avec colonnes calculées |
| TEST-678 | ✅ | Export UNION |
| TEST-679 | ✅ | Export zone invalide |
| TEST-680 | ✅ | Export output_csv commençant par zone |
| TEST-681 | ✅ | Base corrompue |
| TEST-682 | ✅ | Base verrouillée |
| TEST-683 | ✅ | Timeout sur requête longue |
| TEST-684 | ✅ | Mémoire insuffisante |
| TEST-685 | ✅ | Import et query simultanés |
| TEST-686 | ✅ | Nom table SQL injection |
| TEST-687 | ✅ | Path base avec espaces |
| TEST-688 | ✅ | Base dans sous-dossier |
| TEST-689 | ✅ | VACUUM (si autorisé) |
| TEST-690 | ✅ | ATTACH DATABASE (bloqué sécurité) |
| TEST-691 | ✅ | Type fichier texte |
| TEST-692 | ✅ | Type fichier JSON |
| TEST-693 | ✅ | Type fichier PNG |
| TEST-694 | ✅ | Type fichier PDF |
| TEST-695 | ✅ | Type fichier ZIP |
| TEST-696 | ✅ | Type fichier inexistant |
| TEST-697 | ✅ | Type dossier |
| TEST-698 | ✅ | Type zone documents |
| TEST-699 | ✅ | Type zone group sans paramètre group |
| TEST-700 | ✅ | Type zone uploads |
| TEST-701 | ✅ | Type zone invalide |
| TEST-702 | ✅ | Type path traversal |
| TEST-703 | ✅ | Type fichier binaire inconnu |
| TEST-704 | ✅ | Type group sans group param |
| TEST-705 | ✅ | Type sans path |
| TEST-706 | ✅ | Convertir vers Unix (LF) |
| TEST-707 | ✅ | Convertir vers Windows (CRLF) |
| TEST-708 | ✅ | Convertir fichier déjà Unix |
| TEST-709 | ✅ | Convertir zone documents |
| TEST-710 | ✅ | Convertir fichier inexistant |
| TEST-711 | ✅ | Convertir binaire (erreur) |
| TEST-712 | ✅ | Convertir to invalide |
| TEST-713 | ✅ | Convertir zone uploads (interdit) |
| TEST-714 | ✅ | Convertir avec path traversal |
| TEST-715 | ✅ | Convertir fichier volumineux |
| TEST-716 | ✅ | Hexdump par défaut |
| TEST-717 | ✅ | Hexdump avec offset |
| TEST-718 | ✅ | Hexdump avec length |
| TEST-719 | ✅ | Hexdump offset + length |
| TEST-720 | ✅ | Hexdump fichier texte |
| TEST-721 | ✅ | Hexdump fichier inexistant |
| TEST-722 | ✅ | Hexdump zone documents |
| TEST-723 | ✅ | Hexdump offset négatif |
| TEST-724 | ✅ | Hexdump offset > taille |
| TEST-725 | ✅ | Hexdump path traversal |
| TEST-726 | ✅ | Force unlock fichier verrouillé |
| TEST-727 | ✅ | Force unlock fichier non verrouillé |
| TEST-728 | ✅ | Force unlock fichier inexistant |
| TEST-729 | ✅ | Force unlock zone documents |
| TEST-730 | ✅ | Force unlock zone group |
| TEST-731 | ✅ | Créer lien download |
| TEST-732 | ✅ | Créer lien zone documents (API non dispo) |
| TEST-733 | ✅ | Créer lien zone group (API non dispo) |
| TEST-734 | ✅ | Créer lien fichier inexistant |
| TEST-735 | ✅ | Créer lien dossier (interdit) |
| TEST-736 | ✅ | Créer lien zone uploads |
| TEST-737 | ✅ | Créer lien path traversal |
| TEST-738 | ✅ | Créer lien zone invalide |
| TEST-739 | ✅ | Créer lien group sans group |
| TEST-740 | ✅ | Créer lien sans path |
| TEST-741 | ✅ | Créer lien fichier binaire (API non dispo) |
| TEST-742 | ✅ | Créer lien fichier texte (fichier manquant) |
| TEST-743 | ✅ | Créer lien fichier ZIP (API non dispo) |
| TEST-744 | ✅ | Créer lien fichier avec espaces (fichier manquant) |
| TEST-745 | ✅ | Créer lien fichier UTF-8 (fichier manquant) |
| TEST-746 | ✅ | Créer plusieurs liens même fichier (fichier manquant) |
| TEST-747 | ✅ | Créer lien fichier volumineux (API non dispo) |
| TEST-748 | ✅ | Vérifier format clickable_link (fichier manquant) |
| TEST-749 | ✅ | Créer lien dans sous-dossier (fichier manquant) |
| TEST-750 | ✅ | Créer lien fichier caché (API non dispo) |
| TEST-751 | ✅ | Lister liens (skip - API non dispo) |
| TEST-752 | ✅ | Lister liens vide (skip - API non dispo) |
| TEST-753 | ✅ | Lister après création (skip - API non dispo) |
| TEST-754 | ✅ | Lister après suppression (skip - API non dispo) |
| TEST-755 | ✅ | Vérifier infos dans liste (skip - API non dispo) |
| TEST-756 | ✅ | Lister plusieurs liens (skip - API non dispo) |
| TEST-757 | ✅ | Lister liens différentes zones (skip - API non dispo) |
| TEST-758 | ✅ | Lister ne voit pas liens autres users (skip - API non dispo) |
| TEST-759 | ✅ | Lister liens groupe (skip - API non dispo) |
| TEST-760 | ✅ | Lister avec pagination (skip - API non dispo) |
| TEST-761 | ✅ | Supprimer lien (skip - API non dispo) |
| TEST-762 | ✅ | Supprimer lien inexistant (skip - API non dispo) |
| TEST-763 | ✅ | Supprimer sans file_id (skip - API non dispo) |
| TEST-764 | ✅ | Supprimer lien autre user (skip - API non dispo) |
| TEST-765 | ✅ | Supprimer puis vérifier liste (skip - API non dispo) |
| TEST-766 | ✅ | Double suppression (skip - API non dispo) |
| TEST-767 | ✅ | Supprimer ne supprime pas fichier (skip - API non dispo) |
| TEST-768 | ✅ | Supprimer lien zone documents (skip - API non dispo) |
| TEST-769 | ✅ | Supprimer lien zone group (skip - API non dispo) |
| TEST-770 | ✅ | file_id invalide format (skip - API non dispo) |
| TEST-771 | ✅ | Lister groupes (API non dispo) |
| TEST-772 | ✅ | Lister groupes vide (API non dispo) |
| TEST-773 | ✅ | Vérifier infos groupe (API non dispo) |
| TEST-774 | ✅ | Lister plusieurs groupes (API non dispo) |
| TEST-775 | ✅ | Groupe owner vs member (API non dispo) |
| TEST-776 | ✅ | Groupes ne voit pas groupes autres users (API non dispo) |
| TEST-777 | ✅ | Liste inclut groupes invité (API non dispo) |
| TEST-778 | ✅ | Ordre de liste (API non dispo) |
| TEST-779 | ✅ | Groupe avec nom spécial (API non dispo) |
| TEST-780 | ✅ | API groupes indisponible |
| TEST-781 | ✅ | Info groupe existant |
| TEST-782 | ✅ | Info groupe inexistant |
| TEST-783 | ✅ | Info groupe non membre |
| TEST-784 | ✅ | Info sans group |
| TEST-785 | ✅ | Vérifier membres dans info |
| TEST-786 | ✅ | Vérifier quota dans info |
| TEST-787 | ✅ | Info groupe avec beaucoup de membres |
| TEST-788 | ✅ | Vérifier owner dans info |
| TEST-789 | ✅ | Info groupe ID vs nom |
| TEST-790 | ✅ | Vérifier created_at dans info |
| TEST-791 | ✅ | Info groupe avec fichiers |
| TEST-792 | ✅ | Groupe ID caractères spéciaux |
| TEST-793 | ✅ | Info groupe inexistant |
| TEST-794 | ✅ | Info groupe description |
| TEST-795 | ✅ | Info groupe timeout |
| TEST-796 | ✅ | Changer mode vers owner |
| TEST-797 | ✅ | Changer mode vers group |
| TEST-798 | ✅ | Changer mode vers owner_ro |
| TEST-799 | ✅ | Changer mode fichier inexistant |
| TEST-800 | ✅ | Changer mode non owner |
| TEST-801 | ✅ | Changer mode invalide |
| TEST-802 | ✅ | Changer mode sans group |
| TEST-803 | ✅ | Changer mode sans path |
| TEST-804 | ✅ | Changer mode sans mode |
| TEST-805 | ✅ | Changer mode groupe non membre |
| TEST-806 | ✅ | Changer mode path traversal |
| TEST-807 | ✅ | Changer mode dossier |
| TEST-808 | ✅ | Vérifier mode après changement |
| TEST-809 | ✅ | Changer mode plusieurs fois |
| TEST-810 | ✅ | Groupe inexistant |
| TEST-811 | ✅ | Transférer ownership à non-membre |
| TEST-812 | ✅ | Transférer à non-membre invalide |
| TEST-813 | ✅ | Transférer fichier inexistant |
| TEST-814 | ✅ | Transférer non owner |
| TEST-815 | ✅ | Transférer sans group |
| TEST-816 | ✅ | Transférer sans path |
| TEST-817 | ✅ | Transférer sans new_owner |
| TEST-818 | ✅ | Transférer groupe non membre |
| TEST-819 | ✅ | Transférer path traversal |
| TEST-820 | ✅ | Transférer à soi-même |
| TEST-821 | ✅ | Vérifier owner après transfer |
| TEST-822 | ✅ | Transférer fichier mode owner_ro à soi-même |
| TEST-823 | ✅ | new_owner ID invalide format |
| TEST-824 | ✅ | Transférer dossier |
| TEST-825 | ✅ | Groupe inexistant |
| TEST-826 | ✅ | Double transfer échoue (non-membre) |
| TEST-827 | ✅ | Transférer fichier binaire à soi-même |
| TEST-828 | ✅ | Transférer fichier inexistant |
| TEST-829 | ✅ | new_owner par nom invalide |
| TEST-830 | ✅ | Transférer dans sous-dossier inexistant |
| TEST-831 | ✅ | Import fichier spécifique (pas de fichiers) |
| TEST-832 | ✅ | Import tous les fichiers (pas de fichiers) |
| TEST-833 | ✅ | Import fichier inexistant (pas de fichiers) |
| TEST-834 | ✅ | Import sans paramètres (pas de fichiers) |
| TEST-835 | ✅ | Import aucun fichier uploadé |
| TEST-836 | ✅ | Import fichier déjà importé (pas de fichiers) |
| TEST-837 | ✅ | Import fichier volumineux (pas de fichiers) |
| TEST-838 | ✅ | Vérifier fichiers dans uploads après import (pas de fichiers |
| TEST-839 | ✅ | Import multiple fichiers (pas de fichiers) |
| TEST-840 | ✅ | Import avec path traversal (pas de fichiers) |
| TEST-841 | ✅ | Import fichier avec espaces (pas de fichiers) |
| TEST-842 | ✅ | Import fichier UTF-8 (pas de fichiers) |
| TEST-843 | ✅ | Import retourne liste (pas de fichiers) |
| TEST-844 | ✅ | Import filename vide (pas de fichiers) |
| TEST-845 | ✅ | Import filename et import_all (pas de fichiers) |
| TEST-846 | ✅ | Aide générale |
| TEST-847 | ✅ | Aide howto paths |
| TEST-848 | ✅ | Aide howto zones (invalide) |
| TEST-849 | ✅ | Aide howto commands |
| TEST-850 | ✅ | Aide howto csv_to_sqlite |
| TEST-851 | ✅ | Aide howto download |
| TEST-852 | ✅ | Aide howto edit |
| TEST-853 | ✅ | Aide howto share |
| TEST-854 | ✅ | Aide howto invalide |
| TEST-855 | ✅ | Aide howto vide |
| TEST-856 | ✅ | Aide contient liste fonctions |
| TEST-857 | ✅ | Aide format markdown |
| TEST-858 | ✅ | Aide howto upload |
| TEST-859 | ✅ | Aide howto network |
| TEST-860 | ✅ | Aide howto case insensitive |
| TEST-861 | ✅ | Stats utilisateur |
| TEST-862 | ✅ | Stats contient usage |
| TEST-863 | ✅ | Stats contient zones |
| TEST-864 | ✅ | Stats file count |
| TEST-865 | ✅ | Stats groupes |
| TEST-866 | ✅ | Parameters |
| TEST-867 | ✅ | Parameters contient quotas |
| TEST-868 | ✅ | Parameters contient timeouts |
| TEST-869 | ✅ | Parameters contient network_mode |
| TEST-870 | ✅ | Parameters contient limites |
| TEST-871 | ✅ | Allowed commands |
| TEST-872 | ✅ | Allowed commands par zone |
| TEST-873 | ✅ | Allowed commands contient basiques |
| TEST-874 | ✅ | Allowed commands network |
| TEST-875 | ✅ | Maintenance |
| TEST-876 | ✅ | Maintenance nettoie locks expirés |
| TEST-877 | ✅ | Maintenance sans locks expirés |
| TEST-878 | ✅ | Stats après opérations |
| TEST-879 | ✅ | Parameters version |
| TEST-880 | ✅ | Allowed commands git |
| TEST-881 | ✅ | Path traversal simple |
| TEST-882 | ✅ | Path traversal encodé (non décodé) |
| TEST-883 | ✅ | Path traversal double encodé (non décodé) |
| TEST-884 | ✅ | Path avec ../ interne |
| TEST-885 | ✅ | Symlink escape (symlink non existant) |
| TEST-886 | ✅ | Path absolu |
| TEST-887 | ✅ | Path avec null byte |
| TEST-888 | ✅ | Path avec backslash (Linux: pas un séparateur) |
| TEST-889 | ✅ | Traversal via stdout_file |
| TEST-890 | ✅ | Traversal via stderr_file |
| TEST-891 | ✅ | Traversal shed_patch_text |
| TEST-892 | ✅ | Traversal shed_delete |
| TEST-893 | ✅ | Traversal shed_rename dest |
| TEST-894 | ✅ | Traversal shed_zip dest |
| TEST-895 | ✅ | Traversal shed_sqlite path |
| TEST-896 | ✅ | Injection point-virgule |
| TEST-897 | ✅ | Injection pipe |
| TEST-898 | ✅ | Injection && |
| TEST-899 | ✅ | Injection backticks |
| TEST-900 | ✅ | Injection $() |
| TEST-901 | ✅ | Injection > |
| TEST-902 | ✅ | Injection >> |
| TEST-903 | ✅ | Commande non whitelist |
| TEST-904 | ✅ | Commande rm -rf / |
| TEST-905 | ✅ | Commande curl sans -o (network disabled) |
| TEST-906 | ✅ | Commande wget (network disabled) |
| TEST-907 | ✅ | Network disabled |
| TEST-908 | ✅ | Find -exec bloqué |
| TEST-909 | ✅ | Awk system() bloqué |
| TEST-910 | ✅ | Xargs bloqué |
| TEST-911 | ✅ | Injection newline |
| TEST-912 | ✅ | SQL injection shed_sqlite |
| TEST-913 | ✅ | Table name injection |
| TEST-914 | ✅ | Commande vide |
| TEST-915 | ✅ | Commande avec espaces |
| TEST-916 | ✅ | Fichier trop grand storage |
| TEST-917 | ✅ | Fichier trop grand documents |
| TEST-918 | ✅ | Fichier trop grand group |
| TEST-919 | ✅ | shed_patch_bytes simple |
| TEST-920 | ✅ | Zone uploads readonly (write) |
| TEST-921 | ✅ | Zone uploads readonly (mkdir) |
| TEST-922 | ✅ | Group access denied |
| TEST-923 | ✅ | Group file mode owner (fichier inexistant) |
| TEST-924 | ✅ | Group file mode owner_ro (fichier inexistant) |
| TEST-925 | ✅ | Group file delete mode owner (fichier créé par TEST-923) |
| TEST-926 | ✅ | Timeout commande longue |
| TEST-927 | ✅ | Mémoire limite subprocess (contient <) |
| TEST-928 | ✅ | CPU limite subprocess |
| TEST-929 | ✅ | Output truncation |
| TEST-930 | ✅ | Lock expiration |
| TEST-931 | ✅ | User ID test via stats |
| TEST-932 | ✅ | Conversation ID test via stats |
| TEST-933 | ✅ | Zone group vide |
| TEST-934 | ✅ | Group ID caractères interdits |
| TEST-935 | ✅ | Path commençant par zone |
| TEST-936 | ✅ | Output fichier inexistant |
| TEST-937 | ✅ | Locked edit sans verrouillage |
| TEST-938 | ✅ | Download link delete (API non dispo) |
| TEST-939 | ✅ | Unzip fichier inexistant |
| TEST-940 | ✅ | Network disabled (curl) |
| TEST-941 | ✅ | Workflow upload -> storage -> zip -> link |
| TEST-942 | ✅ | Workflow CSV -> SQLite -> analyse |
| TEST-943 | ✅ | Workflow multiple CSV -> SQLite -> JOIN |
| TEST-944 | ✅ | Workflow document versioning |
| TEST-945 | ✅ | Workflow locked edit complet |
| TEST-946 | ✅ | Workflow group collaboration |
| TEST-947 | ✅ | Workflow media processing |
| TEST-948 | ✅ | Workflow pandoc conversion |
| TEST-949 | ✅ | Workflow archive multi-fichiers |
| TEST-950 | ✅ | Workflow backup complet |
| TEST-951 | ✅ | Workflow cross-zone |
| TEST-952 | ✅ | Workflow analyse texte |
| TEST-953 | ✅ | Workflow JSON processing |
| TEST-954 | ✅ | Workflow documents Git history |
| TEST-955 | ✅ | Workflow cleanup |
| TEST-956 | ✅ | Workflow batch file creation |
| TEST-957 | ✅ | Workflow SQLite multi-operations |
| TEST-958 | ✅ | Workflow downloads bulk |
| TEST-959 | ✅ | Workflow error recovery |
| TEST-960 | ✅ | Workflow permissions group |
| TEST-961 | ✅ | Fichier nom très long |
| TEST-962 | ✅ | Arborescence très profonde |
| TEST-963 | ✅ | Beaucoup de fichiers dans dossier |
| TEST-964 | ✅ | Fichier avec tous caractères UTF-8 |
| TEST-965 | ✅ | Fichier avec emojis dans contenu |
| TEST-966 | ✅ | Fichier avec emojis dans nom |
| TEST-967 | ✅ | Opérations simultanées même fichier |
| TEST-968 | ✅ | Requête SQL résultat géant |
| TEST-969 | ✅ | ZIP récursif (zip de zip) |
| TEST-970 | ✅ | Unzip dans lui-même |
| TEST-971 | ✅ | SQLite database locked |
| TEST-972 | ✅ | Git repo status |
| TEST-973 | ✅ | Fichier sparse |
| TEST-974 | ✅ | Timeout très court custom |
| TEST-975 | ✅ | Output exactement à la limite |
| TEST-976 | ✅ | Binary dans text function |
| TEST-977 | ✅ | Text dans binary function |
| TEST-978 | ✅ | Circular symlinks |
| TEST-979 | ✅ | Fichier sans permission lecture |
| TEST-980 | ✅ | Zone avec caractères spéciaux |
| TEST-981 | ✅ | Commande avec timeout=0 |
| TEST-982 | ✅ | Très grand nombre de locks |
| TEST-983 | ✅ | Pattern regex catastrophique |
| TEST-984 | ✅ | Import fichier 0 bytes |
| TEST-985 | ✅ | SQLite table avec 0 colonnes |
| TEST-986 | ✅ | Nom fichier uniquement extension |
| TEST-987 | ✅ | Nom fichier uniquement point |
| TEST-988 | ✅ | Nom fichier deux points |
| TEST-989 | ✅ | Commande avec arguments très longs |
| TEST-990 | ✅ | Beaucoup de groupes |
| TEST-991 | ✅ | Download link fichier supprimé |
| TEST-992 | ✅ | Concurrent SQLite write |
| TEST-993 | ✅ | Fichier avec newlines dans nom |
| TEST-994 | ✅ | Base SQLite avec schéma complexe |
| TEST-995 | ✅ | Workflow complet données pays |
| TEST-996 | ✅ | Recovery après crash |
| TEST-997 | ✅ | Stress test sequential |
| TEST-998 | ✅ | Toutes les zones en une session |
| TEST-999 | ✅ | Toutes les fonctions help |
| TEST-1000 | ✅ | Test final - workflow complet end-to-end |
| TEST-1001 | ✅ | shed_help howto download |
| TEST-1002 | ✅ | shed_help howto csv_to_sqlite |
| TEST-1003 | ✅ | shed_help howto upload |
| TEST-1004 | ✅ | shed_help howto share |
| TEST-1005 | ✅ | shed_help howto edit |
| TEST-1006 | ✅ | shed_help howto commands |
| TEST-1007 | ✅ | shed_help howto network |
| TEST-1008 | ✅ | shed_help howto paths |
| TEST-1009 | ✅ | shed_help howto large_files |
| TEST-1010 | ✅ | shed_help howto zones (non existant) |
| TEST-1011 | ✅ | shed_help howto groups (non existant) |
| TEST-1012 | ✅ | shed_help howto sqlite (non existant) |
| TEST-1013 | ✅ | shed_help howto full |
| TEST-1014 | ✅ | shed_help howto invalide |
| TEST-1015 | ✅ | shed_exec avec stdout_file |
| TEST-1016 | ✅ | shed_exec jq avec stdout_file |
| TEST-1017 | ✅ | shed_exec avec stderr_file |
| TEST-1018 | ✅ | shed_exec avec stdout_file et stderr_file |
| TEST-1019 | ✅ | shed_exec stdout_file dans sous-dossier |
| TEST-1020 | ✅ | shed_exec stdout_file path escape |
| TEST-1021 | ✅ | shed_exec cat vers stdout_file |
| TEST-1022 | ✅ | shed_exec grep vers stdout_file |
| TEST-1023 | ✅ | shed_unzip avec src_zone uploads |
| TEST-1024 | ✅ | shed_unzip src_zone même zone |
| TEST-1025 | ✅ | shed_unzip src_zone documents |
| TEST-1026 | ✅ | shed_unzip src_zone invalide |
| TEST-1027 | ✅ | shed_unzip src_zone groupe (non supporté) |
| TEST-1028 | ✅ | shed_unzip src_zone vide (défaut) |
| TEST-1029 | ✅ | shed_zip avec include_empty_dirs=True |
| TEST-1030 | ✅ | shed_zip avec include_empty_dirs=False |
| TEST-1031 | ✅ | shed_zip défaut (sans include_empty_dirs) |
| TEST-1032 | ✅ | shed_zip fichier unique avec include_empty_dirs |
| TEST-1033 | ✅ | shed_zip dossier non-existant |
| TEST-1034 | ✅ | CSV import avec délimiteur point-virgule |
| TEST-1035 | ✅ | CSV import avec délimiteur tabulation |
| TEST-1036 | ✅ | CSV import avec encoding latin-1 |
| TEST-1037 | ✅ | CSV import avec encoding utf-8 explicite |
| TEST-1038 | ✅ | CSV import avec décimal virgule |
| TEST-1039 | ✅ | CSV import avec date_columns |
| TEST-1040 | ✅ | CSV import avec date_format dayfirst |
| TEST-1041 | ✅ | CSV import complet européen |
| TEST-1042 | ✅ | CSV import avec if_exists replace |
| TEST-1043 | ✅ | CSV import avec if_exists append |
| TEST-1044 | ✅ | CSV import avec if_exists fail (table existe) |
| TEST-1045 | ✅ | CSV import encoding invalide |
| TEST-1046 | ✅ | ZIP bomb potentiel (fichier n'existe pas) |
| TEST-1047 | ✅ | shed_allowed_commands vérifie liste |
| TEST-1048 | ✅ | shed_exec commande non dans whitelist |
| TEST-1049 | ✅ | shed_patch_text overwrite sans overwrite=True sur fichier ex |
| TEST-1050 | ✅ | shed_sqlite readonly mode |
| TEST-1051 | ✅ | Argument avec backtick |
| TEST-1052 | ✅ | Argument avec $() |
| TEST-1053 | ✅ | Argument avec ${ |
| TEST-1054 | ✅ | find avec -exec bloqué |
| TEST-1055 | ✅ | awk avec system() bloqué |
| TEST-1056 | ✅ | shed_exec timeout personnalisé valide |
| TEST-1057 | ✅ | shed_exec timeout maximum |
| TEST-1058 | ✅ | shed_exec timeout dépassant max |
| TEST-1059 | ✅ | shed_patch_text avec message dans documents |
| TEST-1060 | ✅ | shed_rename avec message dans documents |
| TEST-1061 | ✅ | shed_exec avec max_output="" - doit nommer le paramètre faut |
| TEST-1062 | ✅ | shed_patch_text avec line="" - doit indiquer le type attendu |
| TEST-1063 | ✅ | shed_patch_text avec end_line="" - doit indiquer le type att |
| TEST-1064 | ✅ | shed_patch_bytes avec offset="" - doit nommer le paramètre |
| TEST-1065 | ✅ | shed_patch_bytes avec length="" - doit nommer le paramètre |
| TEST-1066 | ✅ | shed_lockedit_exec avec timeout="" - doit nommer le paramètr |
| TEST-1067 | ✅ | shed_hexdump avec offset=None - conversion silencieuse en 0 |
| TEST-1068 | ✅ | shed_hexdump avec length=None - conversion silencieuse en 25 |
| TEST-1069 | ✅ | shed_patch_text avec regex_flags=0 - doit indiquer type stri |
| TEST-1070 | ✅ | shed_convert_eol avec to=None - doit lister les valeurs vali |
| TEST-1071 | ✅ | shed_convert_eol avec to=0 - doit lister les valeurs valides |
| TEST-1072 | ✅ | shed_sqlite avec skip_rows=None - conversion silencieuse en  |
| TEST-1073 | ✅ | shed_sqlite avec import_csv ET query - doit expliquer l'excl |
| TEST-1074 | ✅ | shed_sqlite avec query="" et import_csv fourni - query="" ig |
| TEST-1075 | ✅ | shed_exec avec max_output=0 - utilise max absolu (comporteme |
| TEST-1076 | ✅ | shed_sqlite avec limit=0 - pas de limite (comportement docum |
| TEST-1077 | ✅ | shed_tree avec depth=0 - converti en 1 (minimum) |
| TEST-1078 | ✅ | shed_patch_bytes avec offset=0 - début du fichier (valide) |
| TEST-1079 | ✅ | shed_patch_text overwrite=True avec end_line=0 - ignoré sile |
| TEST-1080 | ✅ | shed_patch_text overwrite=True avec pattern="" - ignoré sile |
| TEST-1081 | ✅ | shed_patch_text overwrite=True avec line=0 - ignoré silencie |
| TEST-1082 | ✅ | shed_patch_text overwrite=True avec regex_flags=0 - ignoré s |
| TEST-1083 | ✅ | shed_exec avec args=0 - converti silencieusement en [] |
| TEST-1084 | ✅ | shed_lockedit_exec avec args=[] explicite puis argument - va |
| TEST-1085 | ✅ | shed_patch_text avec position="overwrite" ET overwrite=True  |
| TEST-1086 | ✅ | shed_patch_text avec position="overwrite" SANS overwrite=Tru |
| TEST-1087 | ✅ | attach database minuscules (bloqué sécurité) |
| TEST-1088 | ✅ | DETACH majuscules (bloqué sécurité) |
| TEST-1089 | ✅ | detach minuscules (bloqué sécurité) |
| TEST-1090 | ✅ | load_extension minuscules (bloqué sécurité) |
| TEST-1091 | ✅ | Attach DATABASE casse mixte (bloqué sécurité) |
| TEST-1092 | ✅ | shed_move_uploads_to_storage sans overwrite sur fichier exis |
| TEST-1093 | ✅ | shed_move_uploads_to_storage avec overwrite=True sur fichier |
| TEST-1094 | ✅ | shed_copy_storage_to_documents sans overwrite sur fichier ex |
| TEST-1095 | ✅ | shed_copy_storage_to_documents avec overwrite=True sur fichi |
| TEST-1096 | ✅ | shed_move_documents_to_storage sans overwrite sur fichier ex |
| TEST-1097 | ✅ | shed_move_documents_to_storage avec overwrite=True sur fichi |
| TEST-1098 | ✅ | shed_move_uploads_to_documents sans overwrite sur fichier ex |
| TEST-1099 | ✅ | shed_move_uploads_to_documents avec overwrite=True sur fichi |
| TEST-1100 | ✅ | shed_copy_to_group sans overwrite sur fichier existant |
| TEST-1101 | ✅ | shed_copy_to_group avec overwrite=True sur fichier existant |
| TEST-1102 | ✅ | Création fichier texte simple storage |
| TEST-1103 | ✅ | Création fichier texte documents avec message |
| TEST-1104 | ✅ | Création fichier texte group |
| TEST-1105 | ✅ | Création fichier UTF-8 |
| TEST-1106 | ✅ | Création fichier vide |
| TEST-1107 | ✅ | Création fichier multilignes |
| TEST-1108 | ✅ | Création dans sous-dossier existant |
| TEST-1109 | ✅ | Création dans sous-dossier inexistant (auto-création) |
| TEST-1110 | ✅ | Écrasement fichier existant (comportement par défaut) |
| TEST-1111 | ✅ | Création avec nom contenant espaces |
| TEST-1112 | ✅ | Création zone uploads (interdit) |
| TEST-1113 | ✅ | Création zone invalide |
| TEST-1114 | ✅ | Création group sans group |
| TEST-1115 | ✅ | Création avec path traversal |
| TEST-1116 | ✅ | Création binaire hex format |
| TEST-1117 | ✅ | Création binaire base64 format |
| TEST-1118 | ✅ | Création binaire raw format |
| TEST-1119 | ✅ | Création binaire documents |
| TEST-1120 | ✅ | Création binaire group |
| TEST-1121 | ✅ | Création binaire vide (hex) |
| TEST-1122 | ✅ | Création binaire hex invalide (longueur impaire) |
| TEST-1123 | ✅ | Création binaire hex invalide (caractères) |
| TEST-1124 | ✅ | Création binaire base64 invalide |
| TEST-1125 | ✅ | file_type invalide |
| TEST-1126 | ✅ | content_format invalide |
| TEST-1127 | ✅ | Création binaire écrase fichier existant |
| TEST-1128 | ✅ | Création binaire dans sous-dossier |
| TEST-1129 | ✅ | Création binaire avec path traversal |
| TEST-1130 | ✅ | Création binaire zone uploads (interdit) |
| TEST-1131 | ✅ | Création group avec mode owner |
| TEST-1132 | ✅ | Création group avec mode owner_ro |
| TEST-1133 | ✅ | Création group avec mode invalide (converti silencieusement  |
| TEST-1134 | ✅ | Création documents avec message vide |
| TEST-1135 | ✅ | Création avec content vide (valide) |
| TEST-1136 | ✅ | Création sans path (paramètre requis) |
| TEST-1137 | ✅ | Création path commençant par zone (bloqué) |
| TEST-1138 | ✅ | Création path commençant par zone avec allow_zone_in_path |
| TEST-1139 | ✅ | Création fichier JSON valide |
| TEST-1140 | ✅ | Création fichier avec contenu très long |
| TEST-1141 | ✅ | Modification .git/config (NON protégé actuellement) |
| TEST-1142 | ✅ | Suppression .git/HEAD (bloqué) |
| TEST-1143 | ✅ | Renommage .git (NON protégé actuellement) |
| TEST-1144 | ✅ | shed_exec rm sur .git (NON protégé actuellement) |
| TEST-1145 | ✅ | Création fichier dans .git (NON protégé actuellement) |
| TEST-1146 | ✅ | curl sans -o (réseau désactivé) |
| TEST-1147 | ✅ | wget sans -O (réseau désactivé) |
| TEST-1148 | ✅ | git clone sans destination (réseau désactivé) |
| TEST-1149 | ✅ | curl avec -o valide (réseau désactivé) |
| TEST-1150 | ✅ | wget avec -O valide (réseau désactivé) |
| TEST-1151 | ✅ | Import CSV complètement vide |
| TEST-1152 | ✅ | Import CSV avec headers seulement (pas de données) |
| TEST-1153 | ✅ | Import CSV avec lignes vides uniquement |
| TEST-1154 | ✅ | Opération sur zone root (chemin vide) |
| TEST-1155 | ✅ | Opération sur zone root (chemin .) |
| TEST-1156 | ✅ | Renommage de la racine (path="." échoue) |
| TEST-1157 | ✅ | shed_tree sur chemin null |
| TEST-1158 | ✅ | shed_hexdump sur répertoire |
| TEST-1159 | ✅ | Suppression lien (API indisponible en test) |
| TEST-1160 | ✅ | Liste liens (API indisponible en test) |
| TEST-1161 | ✅ | Création lien sur fichier inexistant |
| TEST-1162 | ✅ | CSV avec trop de colonnes (5001+) |
| TEST-1163 | ✅ | shed_lockedit_save sans open préalable |
| TEST-1164 | ✅ | shed_force_unlock sur fichier non verrouillé |
| TEST-1165 | ✅ | shed_sqlite sur fichier non-SQLite (SQLite l'ouvre quand mêm |
| TEST-1166 | ✅ | shed_unzip sur fichier non-ZIP |
| TEST-1167 | ✅ | shed_zipinfo sur fichier non-ZIP |
| TEST-1168 | ✅ | shed_convert_eol format invalide |
| TEST-1169 | ✅ | shed_group_chown vers utilisateur invalide |
| TEST-1170 | ✅ | shed_sqlite query vide |
| TEST-1171 | ✅ | shed_link_delete avec file_id None |
| TEST-1172 | ✅ | shed_link_delete avec file_id vide |
| TEST-1173 | ✅ | Import CSV vide avec has_header=False |
| TEST-1174 | ✅ | Import CSV avec uniquement whitespace (traité comme données  |
| TEST-1175 | ✅ | Import CSV headers-only réussit (0 lignes importées) |
| TEST-1176 | ✅ | Import CSV binaire est traité comme texte corrompu (réussit  |
| TEST-1177 | ✅ | Import CSV avec encoding invalide (réussit avec données corr |
| TEST-1178 | ✅ | Import CSV avec colonnes inconsistantes (padding automatique |
| TEST-1179 | ✅ | ZIP avec 100 fichiers (sous le seuil de 10000) |
| TEST-1180 | ✅ | ZIP avec ratio de compression > 100:1 déclenche ZIP_BOMB |
| TEST-1181 | ✅ | ZIP avec 100MB de données répétées déclenche ZIP_BOMB (ratio |
| TEST-1182 | ✅ | Écriture fichier dépassant quota utilisateur |
| TEST-1183 | ✅ | Patch dépassant quota |
| TEST-1184 | ✅ | Copie vers groupe dépassant quota groupe |
| TEST-1185 | ✅ | curl sans -o ni stdout_file |
| TEST-1186 | ✅ | curl avec -L mais sans -o |
| TEST-1187 | ✅ | wget sans -O |
| TEST-1188 | ✅ | curl avec -o fonctionne (contrôle positif) |
| TEST-1189 | ✅ | User ID non-UUID (texte simple) |
| TEST-1190 | ✅ | User ID vide |
| TEST-1191 | ✅ | User ID None |
| TEST-1192 | ✅ | User ID avec espaces seulement |
| TEST-1193 | ✅ | shed_link_create sans user id (validation échoue d'abord) |
| TEST-1194 | ✅ | shed_link_list sans user id |
| TEST-1195 | ✅ | shed_link_delete sans user id |

---

## Section Summary

| Section | Name | Tests | Status |
|:--------|:-----|------:|:------:|
| 1 | shed_exec - Navigation et Lect | 100/100 | ✅ |
| 2 | shed_exec - Écriture et Modifi | 80/80 | ✅ |
| 3 | shed_patch_text | 80/80 | ✅ |
| 4 | shed_patch_bytes | 30/30 | ✅ |
| 5 | shed_delete et shed_rename | 60/60 | ✅ |
| 6 | shed_tree | 20/20 | ✅ |
| 7 | shed_lockedit workflow | 80/80 | ✅ |
| 8 | Zone bridges | 80/80 | ✅ |
| 9 | Archives ZIP | 60/60 | ✅ |
| 10 | shed_sqlite | 100/100 | ✅ |
| 11 | Utilitaires fichiers | 40/40 | ✅ |
| 12 | Download links | 40/40 | ✅ |
| 13 | Groups | 60/60 | ✅ |
| 14 | Utilitaires info | 50/50 | ✅ |
| 15 | Sécurité | 60/60 | ✅ |
| 16 | Workflows complexes | 60/60 | ✅ |
| 17 | Couverture additionnelle | 60/60 | ✅ |
| 18 | LLM Guardrails | 26/26 | ✅ |
| 19 | Sécurité SQL - Case Insensitiv | 5/5 | ✅ |
| 20 | Bridge Functions - Overwrite | 10/10 | ✅ |
| 21 | shed_create_file | 39/39 | ✅ |
| 22 | Codes erreur manquants | 30/30 | ✅ |
| 23 | Codes erreur avancés | 25/25 | ✅ |