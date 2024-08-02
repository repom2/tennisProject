/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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

}
