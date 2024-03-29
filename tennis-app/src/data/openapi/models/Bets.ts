/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type Bets = {
    /**
     * Match ID
     */
    matchId?: string;
    /**
     * Home Player ID
     */
    homeId?: string;
    /**
     * Away Player ID
     */
    awayId?: string;
    /**
     * Home Player Name
     */
    homeName?: string;
    /**
     * Away Player Name
     */
    awayName?: string;
    /**
     * Home Odds
     */
    homeOdds?: number;
    /**
     * Away Odds
     */
    awayOdds?: number;
    /**
     * Home Probability
     */
    homeProb?: number;
    /**
     * Away Probability
     */
    awayProb?: number;
    /**
     * Home yield
     */
    homeYield?: number;
    /**
     * Away yield
     */
    awayYield?: number;
    /**
     * Elo Probability
     */
    eloProb?: number;
    /**
     * Current Year Elo Probability
     */
    yearEloProb?: number;
    /**
     * Home Service Points Won
     */
    homeSpw?: number;
    /**
     * Away Service Points Won
     */
    awaySpw?: number;
    /**
     * Home Return Points Won
     */
    homeRpw?: number;
    /**
     * Away Return Points Won
     */
    awayRpw?: number;
    /**
     * Calculate home win probability based on stats
     */
    statsWin?: number;
    /**
     * Fatigue score for home player
     */
    homeFatigue?: number;
    /**
     * Fatigue score for away player
     */
    awayFatigue?: number;
    /**
     * Head to head win probability
     */
    h2hWin?: number;
    /**
     * Head to head matches
     */
    h2hMatches?: number;
    /**
     * Last match was a retirement
     */
    walkover?: boolean;
    /**
     * How long have not played
     */
    homeInjScore?: number;
    /**
     * How long have not played
     */
    awayInjScore?: number;
    /**
     * Home winning percentage calculated from common opponents
     */
    commonOpponents?: number;
    /**
     * Count of common opponents
     */
    commonOpponentsCount?: number;
    /**
     * Preview
     */
    preview?: string;
    /**
     * Reasoning
     */
    reasoning?: string;
    /**
     * Start time
     */
    startAt?: string;
    /**
     * Home player matches
     */
    homeStatMatches?: number;
    /**
     * Away player matches
     */
    awayStatMatches?: number;
    /**
     * Home player matches
     */
    homeMatches?: string;
    /**
     * Away player matches
     */
    awayMatches?: string;
    /**
     * Home player plays
     */
    homePlays?: string;
    /**
     * Away player plays
     */
    awayPlays?: string;
    /**
     * Home player current rank
     */
    homeCurrentRank?: number;
    /**
     * Away player current rank
     */
    awayCurrentRank?: number;
    /**
     * Home player peak rank
     */
    homePeakRank?: number;
    /**
     * Away player peak rank
     */
    awayPeakRank?: number;
    /**
     * Home player dominance ratio
     */
    homeDr?: number;
    /**
     * Away player dominance ratio
     */
    awayDr?: number;
    /**
     * Home team preview
     */
    homePreview?: string;
    /**
     * Away team preview
     */
    awayPreview?: string;
    /**
     * Home team short preview
     */
    homeShortPreview?: string;
    /**
     * Away team short preview
     */
    awayShortPreview?: string;
    /**
     * Home team table
     */
    homeTable?: string;
    /**
     * Away team table
     */
    awayTable?: string;
    /**
     * Home player info
     */
    homePlayerInfo?: string;
    /**
     * Away player info
     */
    awayPlayerInfo?: string;
    /**
     * Home player AH7.5
     */
    homeAH7_5?: number;
    /**
     * Home player AH6.5
     */
    homeAH6_5?: number;
    /**
     * Home player AH5.5
     */
    homeAH5_5?: number;
    /**
     * Home player AH4.5
     */
    homeAH4_5?: number;
    /**
     * Home player AH3.5
     */
    homeAH3_5?: number;
    /**
     * Home player AH2.5
     */
    homeAH2_5?: number;
    /**
     * away player AH7.5
     */
    awayAH7_5?: number;
    /**
     * away player AH6.5
     */
    awayAH6_5?: number;
    /**
     * away player AH5.5
     */
    awayAH5_5?: number;
    /**
     * away player AH4.5
     */
    awayAH4_5?: number;
    /**
     * away player AH3.5
     */
    awayAH3_5?: number;
    /**
     * away player AH2.5
     */
    awayAH2_5?: number;
    /**
     * Games over 21.5
     */
    gamesOver21_5?: number;
    /**
     * Games over 22.5
     */
    gamesOver22_5?: number;
    /**
     * Games over 23.5
     */
    gamesOver23_5?: number;
    /**
     * Games over 24.5
     */
    gamesOver24_5?: number;
    /**
     * Games over 25.5
     */
    gamesOver25_5?: number;
    /**
     * Home player win single games
     */
    homeWinSingleGame?: number;
    /**
     * Away player win single games
     */
    awayWinSingleGame?: number;
    /**
     * Home player win single sets
     */
    homeWinSingleSet?: number;
    /**
     * Away player win single sets
     */
    awayWinSingleSet?: number;
    /**
     * Home player win 1 set
     */
    homeWin1Set?: number;
    /**
     * Away player win 1 set
     */
    awayWin1Set?: number;
    /**
     * Home player win 2 sets
     */
    homeWin2Set?: number;
    /**
     * Away player win 2 sets
     */
    awayWin2Set?: number;
};

