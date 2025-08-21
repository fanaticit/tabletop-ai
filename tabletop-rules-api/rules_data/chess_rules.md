---
game_id: "chess"
name: "Chess"
publisher: "FIDE"
description: "The classic strategy board game"
complexity: "medium"
min_players: 2
max_players: 2
ai_tags: ["strategy", "board-game", "two-player", "classic"]
---
# Game: Chess

## Rule: Game Overview

**Category**: General

**Complexity**: Basic

**Mandatory**: Yes

Chess is a two-player strategy board game played on an 8×8 grid. Each player begins with sixteen pieces (one king, one queen, two rooks, two bishops, two knights, and eight pawns), and each piece type moves in a unique way. The goal is to checkmate the opponent’s king – that is, to threaten the king with capture in such a way that no legal move can remove the threat【25†Rules of chess.docx】. A game can also end without checkmate, either by a draw (tie) or by one player resigning (conceding the game)【25†Rules of chess.docx】.

Modern chess rules took shape by the early 19th century, after evolving from earlier versions in the Middle Ages【25†Rules of chess.docx】. Today, the official laws of chess are maintained by FIDE (Fédération Internationale des Échecs) and are used internationally, with only minor regional variations【25†Rules of chess.docx】. There are slight rule adjustments for specific chess variants and situations – for example, blitz (fast chess), online chess, correspondence chess, and Chess960 have some special guidelines【25†Rules of chess.docx】. In addition to piece movement, the rules cover standards for equipment, time control, player conduct, accommodations for disabilities, and the recording of moves in notation【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Initial Setup

**Category**: Setup

**Complexity**: Basic

**Mandatory**: Yes

Chess is played on a square board of eight ranks (rows) and eight files (columns) with alternating light and dark squares. The board must be oriented such that each player has a light-colored square at their right-hand corner (“white on right”)【25†Rules of chess.docx】. One player controls the White pieces and the other controls the Black pieces. At the start of the game, White’s pieces are placed on the first rank (nearest White) and pawns on the second rank; Black’s pieces are on the eighth rank (nearest Black) with pawns on the seventh rank【25†Rules of chess.docx】. The initial arrangement of pieces for each side is as follows:

Rooks: on the corner squares (a1 and h1 for White; a8 and h8 for Black).

Knights: on the squares immediately next to the rooks (b1 and g1 for White; b8 and g8 for Black).

Bishops: on the squares immediately next to the knights (c1 and f1 for White; c8 and f8 for Black).

Queen: on the remaining center square of the same color as the piece (White queen on the light square d1; Black queen on the dark square d8)【25†Rules of chess.docx】.

King: on the last remaining center square next to the queen (e1 for White; e8 for Black).

Pawns: on each square of the rank directly in front of the other pieces (White pawns on a2–h2; Black pawns on a7–h7)【25†Rules of chess.docx】.

At the start of play, White always moves first, after which players alternate turns, making one move at a time【25†Rules of chess.docx】. A move consists of moving a single piece (with the exception of castling, which involves moving two pieces in one move). Players are not allowed to skip a turn; if it is a player’s turn, they must make a legal move if one is available【25†Rules of chess.docx】. (If no legal moves are possible and the king is not in check, the result is a stalemate draw – see Draws.) The rules do not prescribe how to decide which player gets the White pieces; this is usually determined by agreement or a random method (such as a coin toss) or set by tournament procedure before the game【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Movement of Pieces

**Category**: Movement

**Complexity**: Basic

**Mandatory**: Yes

**General Movement Rules:** Each type of chess piece moves in a distinct way. In general, a piece may move to any vacant square along its path of movement, or it may capture an opponent’s piece by landing on the occupied square (the captured piece is removed from the board)【25†Rules of chess.docx】. A piece cannot move onto a square occupied by one of its own pieces. Except for the knight (and the special case of castling), pieces cannot jump over other pieces; any piece blocking the path stops movement beyond that point【25†Rules of chess.docx】. (The knight is the only piece that can “leap” over intervening pieces.) When a piece is captured, it is permanently removed from play. Important: A player may not make any move that leaves their own king in check (under attack); such moves are illegal. Note also that while a king can be put in check, the king is never actually captured – the game ends if a checkmate occurs (the king is threatened with no escape)【25†Rules of chess.docx】.

Movement of Each Piece:

King – Moves exactly one square in any direction (horizontally, vertically, or diagonally)【25†Rules of chess.docx】. Special note: the king has a special move called castling that involves moving two squares at once; this is covered under Special Moves.

Queen – Moves any number of vacant squares in any straight line: horizontally, vertically, or diagonally【25†Rules of chess.docx】. This makes the queen the most powerful piece (combining the rook’s and bishop’s movements).

Rook – Moves any number of vacant squares straight horizontally or vertically【25†Rules of chess.docx】. (Rooks also participate in the special castling move with the king.)

Bishop – Moves any number of vacant squares diagonally【25†Rules of chess.docx】. Each bishop stays on the same color square throughout the game (one operates on light squares and the other on dark squares).

Knight – Moves in an “L”-shape: two squares in one direction (horizontal or vertical) and then one square perpendicular to that, or vice versa【25†Rules of chess.docx】. Knights are the only pieces that can jump over other pieces; a knight’s move is not blocked by pieces in between its start and destination squares【25†Rules of chess.docx】.

Each piece captures in the same way it moves (except pawns, which have special capture rules described below). Capturing is done by landing on a square occupied by an opponent’s piece, thereby removing that piece from the board【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Pawn Movement and Promotion

**Category**: Movement

**Complexity**: Intermediate

**Mandatory**: Yes

Pawn Movement: Pawns have more complex movement rules than other pieces【25†Rules of chess.docx】. A pawn moves straight forward one square, provided that square is empty【25†Rules of chess.docx】. On its first move, a pawn also has the option of moving two squares forward (from its starting position), but both squares in front of it must be vacant to do so【25†Rules of chess.docx】. Pawns cannot move backward. Unlike other pieces, a pawn captures differently from how it moves: it captures one square diagonally forward (i.e. one square ahead on a forward-left or forward-right diagonal) if that square is occupied by an enemy piece【25†Rules of chess.docx】. A pawn cannot move diagonally if the target square is empty – diagonal movement is only for capturing. (The only exception is the special en passant capture, which is discussed under Special Moves.)

If a pawn advances two squares on its initial move and lands adjacent to an opposing pawn, it becomes subject to the special en passant capture on the very next move (this rule is explained in detail under Special Moves). Aside from en passant, pawns simply move and capture as described above.

### Promotion

When a pawn reaches the farthest rank (the eighth rank for White pawns, or the first rank for Black pawns), it must be promoted as part of that move【25†Rules of chess.docx】. Upon reaching the last rank, the pawn is removed and is converted into another piece of the player’s choice: a queen, rook, bishop, or knight of the same color【25†Rules of chess.docx】. The choice is not restricted to previously captured pieces – a pawn is usually promoted to a queen (the most powerful piece), but the player may choose a different piece if desired. This means it is theoretically possible for a player to have multiple queens or extra rooks, bishops, or knights on the board at once via promotion【25†Rules of chess.docx】. The promotion is immediate and part of the pawn’s move; the new piece replaces the pawn on the promotion square. There is no limit to the number of pawns that can be promoted in a game (up to nine queens for one side is possible in theory)【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Castling

**Category**: Special Moves

**Complexity**: Intermediate

**Mandatory**: Yes

### Procedure

Castling is a special move that allows a player to move two pieces (the king and one rook) in a single move【25†Rules of chess.docx】. When castling, the king moves two squares toward one of its rooks, and then that rook is moved to the square immediately on the opposite side of the king. Castling can be done on the king’s side (king moves toward the rook on the h-file, known as kingside castling) or on the queen’s side (king moves toward the rook on the a-file, known as queenside castling). For example, White’s kingside castling move consists of moving the white king from e1 to g1 and the rook from h1 to f1. On Black’s queenside, castling would move the black king from e8 to c8 and the rook from a8 to d8. The result of castling is that the king is positioned two squares from its original square, on either the g-file (kingside) or c-file (queenside), with the rook placed on the square immediately next to the king on the opposite side【25†Rules of chess.docx】. Castling counts as a single move (the king and rook move together in one turn).

### Conditions

Castling is only permitted if all of the following conditions are met【25†Rules of chess.docx】:

Neither the king nor the rook involved has previously moved. Both must be unmoved in the game for castling to be legal【25†Rules of chess.docx】. (An unmoved king and rook that are eligible to castle are said to have “castling rights.”)

No pieces between king and rook. All the squares between the king’s starting square and the rook’s starting square must be vacant, so the king and rook have a clear path【25†Rules of chess.docx】.

King not in check. Castling is not allowed if the king is currently in check【25†Rules of chess.docx】.

King does not castle through or into check. The king may not pass through any square that is under attack by an enemy piece, and may not end up on a square under attack. In other words, castling is forbidden if any square the king moves through (the starting square, the square it passes over, or the destination square) is controlled by an opponent’s piece【25†Rules of chess.docx】. (However, it is permitted for the rook to pass through an attacked square, and it’s also permissible if the rook itself is under attack; only the king’s safety matters for this rule.)

If all of the above conditions are satisfied, the player may castle. Castling is typically a valuable move for king safety (moving the king toward the corner and bringing a rook toward the center). Each player can castle only once per game: one with the kingside rook or queenside rook (not both).【25†Rules of chess.docx】

## Rule: En Passant

**Category**: Special Moves

**Complexity**: Intermediate

**Mandatory**: Yes

En passant (French for “in passing”) is a special pawn capture that can occur immediately after an opponent’s pawn makes an initial two-square advance from its starting position【25†Rules of chess.docx】. This rule is designed to prevent a pawn from evading capture by leaping past an adjacent enemy pawn.

Conditions for En Passant: If a pawn moves two squares forward from its starting square and lands directly adjacent to an enemy pawn (side by side on the same rank), the enemy pawn has the right, on its very next move only, to capture the first pawn as if it had moved only one square forward【25†Rules of chess.docx】. This means the enemy pawn moves diagonally into the square that the first pawn passed over, and the first pawn is removed from the board. En passant capture must be performed immediately on the turn following the opposing pawn’s two-square advance; if the opportunity is not taken at that first chance, the right to do so is lost once another move occurs【25†Rules of chess.docx】.

For example, imagine a white pawn on a2 moves two squares to a4, and there is a black pawn on b4 (immediately to its right). On Black’s next turn, the pawn on b4 can move to a3, capturing the white pawn on a4 “in passing.” The white pawn is removed from a4 as if it had only moved to a3 and been captured there【25†Rules of chess.docx】. En passant is only possible under those specific conditions and only with pawns. This capture is a unique exception to the normal movement and capturing rules for pawns and adds an extra tactical consideration in pawn play.【25†Rules of chess.docx】

## Rule: Check

**Category**: Endgame

**Complexity**: Basic

**Mandatory**: Yes

A check occurs when a king is under direct attack by one (or more) of the opponent’s pieces【25†Rules of chess.docx】. If your king is in check, you are required to make a move that ends the threat on your king. In other words, you must get your king out of check on your next turn. There are three possible ways to respond to a check:

Move the King – Move the king to a square where it is not in check (i.e. not under attack by any enemy piece)【25†Rules of chess.docx】.

Capture the Attacking Piece – Move one of your pieces (or the king itself) to capture the opposing piece that is delivering the check, removing the threat【25†Rules of chess.docx】.

Block the Attack – Move one of your pieces in between the attacking piece and your king, if the attacking piece is a sliding piece (rook, bishop, or queen). By interposing a piece, you block the line of attack to the king. (This option does not apply if the checking piece is a knight or pawn, since knights can jump and pawns attack only one square.)【25†Rules of chess.docx】

If a player is in check and none of the above responses are possible, the king is in checkmate and the game ends (see Checkmate rule). It is illegal to make any move that leaves your own king in check【25†Rules of chess.docx】. In practice, if a player has no legal move to get out of check, that means the game is over by checkmate. In casual games, players often say “check” to alert the opponent that their king is under attack, but this is not required by the rules; in fact, announcing "check" is typically discouraged or forbidden in formal tournament play【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Checkmate

**Category**: Endgame

**Complexity**: Basic

**Mandatory**: Yes

A checkmate is the ultimate goal of chess. Checkmate occurs when a player’s king is in check (under attack) and there is no legal move that can remove the king from attack【25†Rules of chess.docx】. In other words, the king is threatened with capture and cannot escape – no move can block, capture the attacker, or move the king to safety. When a king is checkmated, the game ends immediately: the side whose king was checkmated loses, and the opponent wins the game【25†Rules of chess.docx】.

In a checkmate position, the king is not actually captured or removed from the board; the game is simply declared over with the checkmated side losing. For example, a common checkmate scenario is a lone king cornered on the edge of the board by an opponent’s queen and rook – the king is attacked and all its escape squares are covered. As soon as the king is in a position where no move can save it from capture on the next turn, it is checkmate. Delivering checkmate is the primary way to win a chess game【25†Rules of chess.docx】. (If a player’s move delivers checkmate, the game ends at that move – there is no need to play further.)【25†Rules of chess.docx】

## Rule: Resignation

**Category**: Endgame

**Complexity**: Basic

**Mandatory**: No

A player may resign the game at any time if they believe they have little to no chance of winning. Resigning immediately ends the game and is a concession of victory to the opponent【25†Rules of chess.docx】. Typically, a player resigns by saying “I resign” or by gently laying down their king on the board. (Simply stopping the chess clock is not an official signal of resignation, as clocks can be paused for other reasons like calling an arbiter【25†Rules of chess.docx】.) Offering a handshake can accompany a resignation, but be mindful that a handshake could also be interpreted as an offer of a draw if not clear, so verbal confirmation is preferred【25†Rules of chess.docx】.

In formal rules, when a player resigns, the opponent is awarded a win. Exception: Under FIDE rules, if a player resigns at a moment when the opponent has no theoretical way to ever checkmate (for example, the opponent only has a lone king remaining), then the game is scored as a draw rather than a win【25†Rules of chess.docx】. (This situation is rare, as normally a player would not resign if the opponent has insufficient material, but the rule covers that edge case.) In all other cases, a resignation is recorded as a loss for the resigning player and a win for the opponent【25†Rules of chess.docx】. Resignation is not mandatory, but it is a common practice to concede in hopeless positions rather than play on until checkmate.【25†Rules of chess.docx】

## Rule: Draws

**Category**: Draws

**Complexity**: Intermediate

**Mandatory**: Yes

Not all chess games end with a win or loss; many games end in a draw (a tie). The official rules recognize several conditions under which a game is drawn【25†Rules of chess.docx】:

Stalemate – If a player is not in check but has no legal moves available on their turn, the position is a stalemate and the game is drawn【25†Rules of chess.docx】. (For example, a lone king not in check but unable to move anywhere safe results in stalemate.)

Dead Position (Insufficient Material) – The game is immediately drawn if a position arises in which no sequence of legal moves could lead to a checkmate for either side【25†Rules of chess.docx】. This typically occurs when there is insufficient material to force a mate. Common cases of a dead position are when both players have only their kings left, or king vs. king and bishop, king vs. king and knight, or king and bishop vs. king and bishop of the same color, etc., where checkmate is impossible【25†Rules of chess.docx】. A completely blocked position with no possibility of progress for either side can also be declared a dead position.

Draw by Agreement – At any point in the game, a player may offer a draw, and if the opponent accepts, the game is drawn by mutual agreement【25†Rules of chess.docx】. (In competitive play, a draw offer is typically made verbally or by pausing the clock and must be recorded on the scoresheet with an “=” sign【25†Rules of chess.docx】.)

Fifty-Move Rule – If 50 consecutive moves by each player (50 moves each, 100 moves total) occur without any pawn move or any capture, either player may claim a draw under the fifty-move rule【25†Rules of chess.docx】. This rule is in place to prevent interminable games when no progress is being made.

Threefold Repetition – If the same exact position (with the same player to move and same rights such as castling or en passant eligibility) occurs three times in the game (not necessarily consecutively), either player may claim a draw【25†Rules of chess.docx】. The repetitions do not have to occur back-to-back; a player can claim a draw when the position is about to repeat for the third time (or has just repeated for the third time). This rule covers situations like perpetual check or other repeating sequences.

Impossibility of Checkmate / Insufficient Mating Material on Time – If a player’s time runs out or a player resigns but their opponent has no possible way to ever checkmate with the material remaining, the game is declared a draw rather than a win for the other player【25†Rules of chess.docx】. For example, if Player A’s flag falls (time expires) but Player B has only a lone king (which cannot deliver checkmate by itself), the result is a draw. Similarly, as noted under Resignation, if a player resigns in a position where the opponent has insufficient material to mate, the result is a draw.

Note: Under current FIDE laws, a fivefold repetition of position or seventy-five moves without a capture or pawn move will automatically result in a draw, even without a claim by a player【25†Rules of chess.docx】. (These are extensions of the threefold repetition and fifty-move rules to cover cases where players might not claim the draw.) Also, there is no longer any separate rule for “perpetual check” – a scenario of endless checks will eventually fall under the threefold repetition or fifty-move rule conditions if it continues【25†Rules of chess.docx】.

Note: The United States Chess Federation (USCF) has an additional rule called “insufficient losing chances” in certain fast time control games. It allows a player with a clearly drawn (but not yet dead) position to claim a draw on the basis that the opponent has no realistic chance to win, even if a theoretical mate is possible only with the opponent’s cooperation【25†Rules of chess.docx】. This is a specialized tournament rule not used in FIDE play.【25†Rules of chess.docx】

## Rule: Touch-Move Rule

**Category**: Competitive Play

**Complexity**: Intermediate

**Mandatory**: No

In official chess play, the touch-move rule is enforced to maintain discipline in moving pieces. According to this rule, if a player intentionally touches one of their pieces on the board when it is their turn to move, they must move that piece if it has any legal move available【25†Rules of chess.docx】. If a player touches one of the opponent’s pieces, they must capture that piece if a legal capture is possible. In essence, once you deliberately touch a piece, you commit to moving or capturing with that piece. The touch-move rule prevents players from “experimenting” on the board by adjusting or hesitating with pieces.

There is an important exception for adjusting pieces on their squares: a player who wishes to adjust a piece’s placement (for example, centering it on the square) without the intention to move it must first announce “J’adoube” (French for “I adjust”) or state “adjust” before touching the piece【25†Rules of chess.docx】. This alerts the opponent that the touch is not a move attempt. You may only adjust pieces on your turn (the player who has the move is the only one allowed to touch the pieces, and only with proper announcement)【25†Rules of chess.docx】.

### Special Cases and Piece Handling

Players must move pieces with one hand. You cannot use both hands to make a single move (for example, moving two pieces at once during castling must be done sequentially with the same hand)【25†Rules of chess.docx】. Once you release a piece after moving it, the move is considered completed (if the move was legal) and cannot be retracted【25†Rules of chess.docx】. If a move was illegal, see Irregularities for how to proceed.

When castling, the player should touch and move the king first, then move the rook【25†Rules of chess.docx】. If a player accidentally moves the rook before the king while castling, it is still required that the king move first; in practice, the arbiter may allow the move to be corrected to king-first. (Touching the rook first in an attempt to castle can technically invoke the touch-move rule on the rook. Tournament rules often specify that castling must be done by king move followed by rook move with one hand to avoid confusion.)【25†Rules of chess.docx】

In pawn promotion, if a pawn reaches the last rank and the player removes the pawn from the board or releases it on the final square, that pawn must be promoted – the player cannot choose to take back the pawn move【25†Rules of chess.docx】. The player then selects a replacement piece (queen, rook, bishop, or knight) and places it on the promotion square to complete the move. The promotion is not finalized until the new piece is placed on that square; the pawn’s move to the last rank and the placement of the new piece are considered part of one move【25†Rules of chess.docx】. In official play, using an upside-down rook to represent a queen (a common informal practice if an extra queen piece is not immediately available) is not accepted – an inverted rook on the board is treated as a rook by the rules【25†Rules of chess.docx】. If the correct piece is not available, the player should stop the clock and summon an arbiter to provide the proper piece for promotion【25†Rules of chess.docx】.

In summary, the touch-move rule requires careful intention: once you touch a piece on your turn (aside from adjusting with announcement), you must move it if you can. This rule, along with the procedures for castling and promotion, ensures moves are made cleanly and without ambiguity in competitive play【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Time Control and Clocks

**Category**: Competitive Play

**Complexity**: Intermediate

**Mandatory**: No

In competitive chess, games are often played with a time control, meaning each player has a limited amount of time to make their moves. A chess clock is used to track each player’s remaining time【25†Rules of chess.docx】. The clock usually has two timers—one for each player—that count down only while that player is on move. There are various types of time controls: for example, “40 moves in 90 minutes plus 30 minutes to finish, with a 30-second increment per move” is a common format for long games, while rapid and blitz games use much shorter total times (e.g. 10 minutes each for rapid, 5 minutes or less for blitz) often with no additional periods【25†Rules of chess.docx】. Some clocks use a delay or increment – giving extra seconds per move to the player – to reduce time-pressure issues. If a game is played without an increment or delay, it’s called a “sudden death” time control (all moves must be made within the set time).

**Running out of time:** If a player uses up all of the allotted time on their clock, this is called “flag-fall” (referring to older analog clocks that had a small flag that would drop). In principle, if a player’s time runs out, that player loses the game on time【25†Rules of chess.docx】. However, there is an important exception: if the opponent does not have the material to possibly checkmate, then a timeout results in a draw instead of a loss. For instance, if Player A’s time expires but Player B has only a king and a knight (which cannot force checkmate against a lone king), the game is drawn due to insufficient mating material【25†Rules of chess.docx】. Under FIDE rules, it is enough that a checkmate is theoretically possible with the material on board (it doesn’t have to be forced); if so, the win on time stands【25†Rules of chess.docx】. Under USCF (United States) rules, the standard is stricter: to claim a win on time, the opponent must have sufficient material to force a win. USCF rules enumerate combinations like lone king, king + bishop, king + knight (and king + two knights vs king with no pawns) as “insufficient material to win on time,” resulting in a draw if time runs out【25†Rules of chess.docx】. (One famous example involved a player flagging with a lone knight vs a lone knight – under FIDE that’s a draw since mate is impossible; with certain USCF rules, king + knight vs king + knight would also be a draw on time because no forced mate exists.)

**Claiming a win or draw on time:** In tournament play, the arbiter or the players must notice the flag fall. If a player’s flag falls and the opponent points it out (or an arbiter observes it), the game can be claimed as a win (or draw if the insufficient material exception applies) for the opponent【25†Rules of chess.docx】. If both players’ flags have fallen on analog clocks, it can be ambiguous who lost on time; with digital clocks, the device usually shows which flag fell first【25†Rules of chess.docx】. If a checkmate position arises on the board before the flag fall is claimed or noticed, checkmate takes precedence (the game is a win by checkmate, regardless of the clock)【25†Rules of chess.docx】. Similarly, if a draw condition (such as stalemate, dead position, threefold repetition, or the fifty-move rule) arises before a flag claim, the game is drawn, even if a clock later shows time expired【25†Rules of chess.docx】. In summary, the sequence of events is important: once a game-ending condition on the board occurs, the result is decided by that condition, not by any subsequent flag fall. Conversely, if time runs out first and it’s properly claimed, that decides the game (barring the no-mate-material scenario).

**Quickplay Finish rules:** In the last phase of games without increment (e.g., when both players are under 2 minutes in a sudden-death finish), FIDE rules provide special options. A player with very little time who believes the opponent is not attempting to win by normal means (just running the clock) or that no progress can be made may claim a draw with the arbiter, or request that a small time increment be introduced【25†Rules of chess.docx】. These are called quickplay finish rules. With modern digital clocks and the use of increment time controls, such situations are less common, but the rules exist mainly for games on analog clocks or where no increment is used【25†Rules of chess.docx】.

Overall, time management is a critical aspect of competitive chess. Players must balance playing good moves with the necessity of not running out of time, making the chess clock as important as the board in tournament play【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Recording Moves (Chess Notation)

**Category**: Competitive Play

**Complexity**: Intermediate

**Mandatory**: No

In official games, players are generally required to record the moves of the game using a standard notation system. The most common system is algebraic chess notation. In algebraic notation, each square of the board is identified by a unique coordinate: files (columns) are labeled a through h from White’s left to right, and ranks (rows) are numbered 1 through 8 starting from White’s side of the board【25†Rules of chess.docx】. For example, the square at White’s lower-right corner is “h1,” the square at Black’s lower-right corner is “h8,” and White’s king starts on e1 while Black’s king starts on e8【25†Rules of chess.docx】. Each move is then recorded by the piece abbreviation and the square it moves to (with additional notation for captures, check, etc., which are standard but not detailed here). For instance, a move might be recorded as e4 (meaning a pawn moved to e4) or Nf3 (knight moved to f3).

During a competition game, both players must keep a written record of the game (called a scoresheet) by writing down each move as it is played【25†Rules of chess.docx】. This record is important for several reasons: it allows players to later review the game, and it is used to resolve certain disputes or claims (for example, proving a threefold repetition or fifty-move rule claim, or checking whether an illegal move was made sometime earlier)【25†Rules of chess.docx】. If a player has less than five minutes remaining in a time period and no increment of 30 seconds or more is in effect, that player is typically relieved of the obligation to record moves until the time control is passed or the game is finished【25†Rules of chess.docx】. (In other words, during a severe time scramble with no increment, players can stop keeping score, though the arbiter may require the reconstruction of the moves afterwards if needed.) In games with increment time, players are expected to continue recording moves even in the final minutes.

Players should make sure their scoresheet is up-to-date and legible. Both players’ scoresheets must be available to the arbiter or tournament director upon request【25†Rules of chess.docx】. If a player offers a draw, it is customary to record “=”(equals sign) next to that move on the scoresheet as a record of the offer【25†Rules of chess.docx】. Only algebraic notation is accepted in most modern tournaments; older notation systems (like descriptive notation) are not accepted for rule claims or evidence. The current FIDE rule also specifies that a player should make a move on the board before writing it down on paper (no writing moves in advance)【25†Rules of chess.docx】. Recording moves is an important part of competitive chess protocol and is mandated to ensure fairness and accuracy in play【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Adjournment

**Category**: Competitive Play

**Complexity**: Advanced

**Mandatory**: No

An adjournment is a procedure to pause and resume a chess game at a later time. Adjournments were once common in long tournament games (for example, when games lasted many hours and needed to be postponed to the next day), but they are now rarely used in modern events【25†Rules of chess.docx】. With the advent of faster time controls and anti-cheating measures, most tournaments play games to completion without interruption. However, the official rules still provide for adjournments in the case they are needed (such as in some correspondence or formal matches).

When a game is adjourned, the player whose turn it is does not make their move on the board. Instead, they secretly write down their intended next move on a piece of paper – this is called the sealed move【25†Rules of chess.docx】. The arbiter takes this sealed move, places it in an envelope, and also notes the current board position, the time remaining on each player’s clock, which player is to move, and other relevant details on the envelope【25†Rules of chess.docx】. The envelope is then sealed and signed by the arbiter (and often by the players) to ensure it is not tampered with.

The game is then paused (adjourned) and the players will resume at a specified later time. When the game is resumed, the sealed envelope is opened by the arbiter. The move inside (the sealed move) is made on the board, and the opponent’s clock is started – now the game continues normally from that position【25†Rules of chess.docx】. Both players get their remaining allotted time on the clock to finish the game.

It’s important that the sealed move be clear and unambiguous; if the sealed move is illegal or unclear, there are rules to handle that situation (usually it counts as an illegal move if not resolvable). Adjournments were primarily used to allow players to rest or to avoid extremely long sessions. In modern practice, adjournments are no longer standard – most competitions use time controls that ensure the game finishes in one sitting, or use tie-break methods rather than adjourn. With concerns about computer assistance, adjournments have fallen out of favor in high-level play【25†Rules of chess.docx】. They survive mainly in some correspondence chess contexts or exceptional situations.【25†Rules of chess.docx】

## Rule: Illegal Moves and Penalties

**Category**: Competitive Play

**Complexity**: Advanced

**Mandatory**: Yes

An illegal move is a move that violates the rules of chess. This includes moving a piece in a way that is not allowed for that piece, leaving one’s king in check (or moving it into check), or otherwise contravening any rule (for example, moving a rook like a knight, or a pawn backward, etc.)【25†Rules of chess.docx】. In tournament settings, certain actions like pressing the clock without making a move or using two hands to make a move (e.g., moving the king and rook simultaneously during castling) are also considered illegal moves or illegal actions【25†Rules of chess.docx】. Making an illegal move has consequences: the move must be corrected, and repeated offenses incur penalties.

Rectifying an Illegal Move: If a player makes an illegal move and the mistake is noticed immediately (by either player or an arbiter), the illegal move must be retracted and a legal move substituted with the same piece if a legal move with that piece is available【25†Rules of chess.docx】. The game is then continued from the corrected position. For example, if a player accidentally moves their bishop like a knight, this is illegal; it must be taken back and a correct move with that bishop (if possible) must be played instead. If the illegal move involved a sequence like an improper castling (say the king was in check or moved through check), then the touch-move rule applies to the king (the king must make another legal move if one exists, but the rook is not forced to move since castling was invalid)【25†Rules of chess.docx】.

If an illegal move is discovered later in the game, the rules prescribe that the game should be reset to the position just before the illegal move occurred, and then play resumes from there with the clocks adjusted as appropriate to undo any time gained or lost【25†Rules of chess.docx】. All moves played after the illegal move are void. If the exact position cannot be reconstructed, the game reverts to the last known correct position. These corrections usually require an arbiter’s assistance.

Penalties for Illegal Moves (FIDE rules): Modern chess rules assign penalties to discourage illegal moves, especially in fast time controls. Under FIDE Laws of Chess【25†Rules of chess.docx】:

The first illegal move by a player typically results in a time penalty to that player. In standard (long) games, two extra minutes are added to the opponent’s clock【25†Rules of chess.docx】. In rapid or blitz games, usually one extra minute is added to the opponent’s time. The arbiter will correct the position as described above and add the time to the non-offending player.

The second illegal move by the same player usually results in an immediate loss of the game for that player【25†Rules of chess.docx】 (unless the position is such that the opponent cannot possibly checkmate with any sequence of legal moves, in which case the game is drawn instead of a win – for example, if a player commits a second illegal move but the opponent only has a lone king, the result would be a draw)【25†Rules of chess.docx】.

A move is considered “completed” when a player has made their move and pressed their clock. If an illegal move is noticed before the player presses the clock (and they rectify it themselves in standard play), they can usually correct it without penalty – the move never completed. In blitz/rapid games, if an illegal move is noticed after the opponent has made a subsequent move, the illegal move generally stands (no retroactive correction) because the opportunity to claim it has passed【25†Rules of chess.docx】. This means in blitz chess, players must claim an illegal move immediately.

USCF differences: Under USCF rules for blitz, if a player makes an illegal move, the opponent may immediately claim a win on that basis before making their own next move【25†Rules of chess.docx】. One common way to do this is by stopping the clocks and pointing out the illegal move; another is that the opponent can even take the king that was left in check as proof of the illegal position. If the opponent does not claim the win and instead makes a move, the illegal move is accepted as part of the game and cannot be rolled back after the fact【25†Rules of chess.docx】. (Also, USCF might not use the two-move loss rule in blitz; instead, a single illegal move can lose if claimed.)

In summary, players are expected to be vigilant and avoid illegal moves. If an illegal move happens, it should be corrected promptly. Repeated illegal moves lead to stringent penalties to preserve the integrity of the game【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Board Irregularities

**Category**: Competitive Play

**Complexity**: Advanced

**Mandatory**: No

This section covers various irregularities in the initial setup or during the game (other than moves) and how to resolve them according to the rules【25†Rules of chess.docx】:

Incorrect Initial Setup: If it is discovered during a game that the pieces were not set up in the correct initial position (for example, a knight and bishop were swapped, or a pawn missing, etc.), the game is stopped and restarted from the correct starting position with the same arrangement of who is White and Black【25†Rules of chess.docx】. If the board was placed incorrectly (e.g., a dark square is on each player’s right-hand side instead of a light square), then the game is paused and the board is reoriented correctly; the pieces are transferred to the proper squares on the correctly oriented board, and the game continues from the same position (this does not require restarting the game)【25†Rules of chess.docx】. If the players inadvertently started the game with the colors reversed (each playing the opposite color than assigned), the rules say: if this is noticed within the first 10 moves of the game, the game should be restarted with correct colors; if discovered after 10 moves have been played, the game continues with the colors as is (the mistake is left uncorrected)【25†Rules of chess.docx】.

Clock Setting Errors: If an incorrect time or improper setting was configured on the chess clock and this is noticed during the game, the arbiter should correct the clock to the proper setting based on the best information available and then continue the game【25†Rules of chess.docx】.

Piece Displacement: If during play some pieces are accidentally knocked over or displaced (for example, a player bumps the board), the responsibility lies with the player who caused the displacement to restore the pieces to their correct positions on their own time【25†Rules of chess.docx】. Both players should cooperate to reconstruct the position accurately. If it’s unclear where some pieces should go and the position can’t be reliably recovered, the game should be reset to the last known correct position. In any case, the clocks may be adjusted to compensate for the interruption as determined by the arbiter.

Discovered Illegal Arrangement: If at any point it’s found that the pieces are in an illegal position – meaning a position that could not be reached by any series of legal moves (for example, two white bishops on the same color square, or a pawn arrangement impossible without illegal moves) – then an irregularity has occurred earlier. The game should be brought back to the last known legal position and resumed from there【25†Rules of chess.docx】. An illegal position is typically the result of an unnoticed illegal move or misplaced piece earlier in the game. The arbiter will help determine the correct restoration.

In all cases of irregularities, the arbiter (tournament director) should be notified to make a ruling and assist in correcting the situation. The aim is to resume play in a fair way from a correct position. Minor issues like board orientation or clock settings are fixed and play continues, whereas major setup errors early on lead to restarting the game. These rules ensure that the game state remains valid and fair even if human errors occur before or during the game【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Conduct and Etiquette

**Category**: Competitive Play

**Complexity**: Intermediate

**Mandatory**: No

Players in a chess game are expected to adhere to standards of good conduct and sportsmanship. The official rules include guidelines on behavior to ensure a fair and respectful playing environment【25†Rules of chess.docx】:

No Outside Assistance: During a game, players must not use notes, reference materials, or receive advice from other people or from chess engines/computers【25†Rules of chess.docx】. Analysis on another board or electronic device is strictly prohibited while the game is in progress. A player’s scoresheet is meant only for recording moves, clock times, draw offers, and similar objective information – not for writing down analysis or reminders【25†Rules of chess.docx】.

Respectful Behavior: Players should conduct themselves with courtesy. It’s traditional to shake hands before and after a game as a sign of respect. During play, conversation is generally not allowed. A player should not talk to their opponent (or others) except as necessary – for example, to offer a draw, resign, or to summon the arbiter if an issue arises【25†Rules of chess.docx】. Distracting the opponent in any way is forbidden: this includes making noises, frequently offering draws to annoy the opponent, or any kind of disturbance【25†Rules of chess.docx】. In informal games, announcing “check” when you attack the enemy king is a common courtesy, but in formal games it is not required and is usually discouraged to avoid distraction【25†Rules of chess.docx】. Essentially, players must not interfere with the opponent’s concentration.

Leaving the Board: A player should not leave the playing area without the arbiter’s permission when their game is in progress【25†Rules of chess.docx】. This is to prevent situations like seeking outside help or abandoning the game unfairly. If a player needs to leave temporarily (for a restroom break, for instance), they should inform an arbiter.

Electronic Devices: The use of mobile phones or electronic devices is heavily restricted. Mobile phones must be turned off in the playing venue. If a player’s phone rings, makes noise, or if the player is found using a phone (or any unauthorized electronic aid) during the game, the penalty is typically forfeiture of the game (an automatic loss)【25†Rules of chess.docx】. In fact, FIDE rules since 2014 state that players are not allowed to have a phone on their person in the playing area at all; even having a phone that emits a sound can result in loss of the game【25†Rules of chess.docx】. Tournament rules may specify some leeway for minor events, but in top-level competitions the rule is very strict due to cheating concerns. The first high-profile case of a forfeit due to a ringing phone occurred in 2003, and since then rules have become even stricter【25†Rules of chess.docx】.

Ethics: High standards of ethics are expected. Cheating in any form is obviously forbidden. Also, players should not agree to maneuvers that contravene the competition’s rules (for example, pre-arranging results or draws in a manner not allowed by the tournament). Both players are expected to do their best to abide by the rules and the spirit of fair play. Unsportsmanlike conduct (such as taunting, refusing to shake hands, or deliberately distracting the opponent) can be penalized by the arbiter.

In summary, apart from knowing the moves, chess players in competition must also observe these conduct rules. They are designed to ensure that the game is decided solely by the skill of the players on the board, without outside influence or unfair behavior, and that both players treat each other with respect【25†Rules of chess.docx】.【25†Rules of chess.docx】

## Rule: Equipment

**Category**: Setup

**Complexity**: Intermediate

**Mandatory**: No

Chess equipment used in official play must meet certain standards set by the rules【25†Rules of chess.docx】:

Chess Pieces: The standard design of pieces for tournament play is the Staunton pattern. Pieces are typically made of wood or plastic and come in two contrasting colors traditionally referred to as “white” and “black” (often one side is a light color like cream or natural wood, and the other side a dark color like brown, black, or red—regardless, they are called white and black)【25†Rules of chess.docx】. The size of the pieces is regulated: the king should be about 95 mm (approximately 3.75 inches) in height (with a tolerance of about 10%), and other pieces are proportioned accordingly【25†Rules of chess.docx】. The king’s base diameter is typically about 40-50% of its height【25†Rules of chess.docx】, and other pieces should have base sizes in proportion to the king. Pieces should be well balanced, meaning weighted at the base so they stand stable on the board【25†Rules of chess.docx】. In competition, having two queens of each color is recommended (for pawn promotions), or an extra queen can be provided if needed.

Chessboard: The board is an 8×8 grid of 64 squares, alternately light and dark colored. Tournament boards are commonly wood or vinyl. The square size should be such that pieces fit comfortably: the side of each square is about 1.25 to 1.3 times the diameter of the base of the king【25†Rules of chess.docx】. In practice, for a king ~95 mm tall with base ~45 mm, square size of about 50 to 65 mm (2 to 2.5 inches) is appropriate【25†Rules of chess.docx】. A common standard size is ~57 mm (2.25 inches) per square, which accommodates most Staunton pieces in the preferred size range【25†Rules of chess.docx】. As a guideline, four pawns side by side should fit within one square’s width【25†Rules of chess.docx】. The board’s colors can vary (e.g., light brown vs dark brown, or white vs green, etc.), but they must be clearly distinguishable as light and dark. Typically the lighter-colored squares are called “white.” The board must be placed with a light square at each player’s right-hand corner (as noted in setup).

Chess Clock: A chess clock (with two timers) is used when games are played with time limits【25†Rules of chess.docx】. Clocks can be analog or digital, though digital clocks are now standard in most events because they can handle increments/delays and show precise timings. The clock is not part of the board per se, but it is essential equipment for timed games. Clock rules (starting the clock, stopping it, etc.) are covered under time control regulations.

All equipment should be standardized to ensure fairness – for example, both players’ queens should be identical in shape and size, etc. Tournament organizers typically provide the boards, pieces, and clocks that meet these specifications. The Staunton pieces and proper board size help avoid any ambiguity in piece recognition and allow players to comfortably move pieces without knocking others over. Deviations (like oddly shaped pieces or incorrect sizes) are not used in official play【25†Rules of chess.docx】. Players in casual play can use any chess set, but competitive play adheres to these equipment standards for consistency and clarity.【25†Rules of chess.docx】
