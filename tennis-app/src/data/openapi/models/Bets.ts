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
};

