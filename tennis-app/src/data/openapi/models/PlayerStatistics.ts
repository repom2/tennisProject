/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type PlayerStatistics = {
    /**
     * Service Points Won
     */
    playerSPW?: number;
    /**
     * Return Points Won
     */
    playerRPW?: number;
    /**
     * Matches Played
     */
    playerMatches?: number;
    matches?: {
        date?: Array<string>;
        surface?: Array<string>;
        round_name?: Array<string>;
        tourney_name?: Array<string>;
        spw?: Array<number>;
        rpw?: Array<number>;
    };
};

