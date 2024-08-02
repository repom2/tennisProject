/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MatchProbabilities } from '../models/MatchProbabilities';
import type { PlayerStatistics } from '../models/PlayerStatistics';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class StatisticsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Get player statistics
     * @returns PlayerStatistics Success
     * @throws ApiError
     */
    public getPlayerStatistics({
        level,
        playerId,
        surface,
    }: {
        /**
         * League level
         */
        level?: string,
        /**
         * Player ID
         */
        playerId?: string,
        /**
         * Surface
         */
        surface?: string,
    }): CancelablePromise<PlayerStatistics> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/player-statistics',
            query: {
                'level': level,
                'playerId': playerId,
                'surface': surface,
            },
            errors: {
                404: `Player statistics not found`,
            },
        });
    }

    /**
     * Get match probabilities
     * @returns MatchProbabilities Success
     * @throws ApiError
     */
    public getMatchProbabilities({
        tourName,
        homeSpw,
        surface,
        homeRpw,
        awayRpw,
        awaySpw,
    }: {
        /**
         * Tournament Name
         */
        tourName?: string,
        /**
         * Home Service Points Won
         */
        homeSpw?: number,
        /**
         * Surface
         */
        surface?: string,
        /**
         * Home Return Points Won
         */
        homeRpw?: number,
        /**
         * Away Return Points Won
         */
        awayRpw?: number,
        /**
         * Away Service Points Won
         */
        awaySpw?: number,
    }): CancelablePromise<MatchProbabilities> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/match-probs',
            query: {
                'tourName': tourName,
                'homeSPW': homeSpw,
                'surface': surface,
                'homeRPW': homeRpw,
                'awayRPW': awayRpw,
                'awaySPW': awaySpw,
            },
            errors: {
                404: `Match probabilities not found`,
            },
        });
    }

}
