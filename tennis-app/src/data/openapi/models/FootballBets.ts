/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type FootballBets = {
    /**
     * Match ID
     */
    matchId?: string;
    /**
     * Home Team ID
     */
    homeId?: string;
    /**
     * Away Team ID
     */
    awayId?: string;
    /**
     * Home Team Name
     */
    homeName?: string;
    /**
     * Away Team Name
     */
    awayName?: string;
    /**
     * Home Odds
     */
    homeOdds?: number;
    /**
     * Draw Odds
     */
    drawOdds?: number;
    /**
     * Away Odds
     */
    awayOdds?: number;
    /**
     * Home Probability
     */
    homeProb?: number;
    /**
     * Draw Probability
     */
    drawProb?: number;
    /**
     * Away Probability
     */
    awayProb?: number;
    /**
     * Home yield
     */
    homeYield?: number;
    /**
     * Draw yield
     */
    drawYield?: number;
    /**
     * Away yield
     */
    awayYield?: number;
    /**
     * Elo Probability
     */
    eloProb?: number;
    /**
     * Home and Away Elo Probability
     */
    eloProbHome?: number;
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
     * Home team preview
     */
    homePreview?: string;
    /**
     * Away team preview
     */
    awayPreview?: string;
};

