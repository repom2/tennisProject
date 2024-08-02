/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EloRatings } from '../models/EloRatings';
import type { Players } from '../models/Players';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class PlayersService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Get players
     * @returns Players Success
     * @throws ApiError
     */
    public getPlayers({
        level,
    }: {
        /**
         * League level
         */
        level?: string,
    }): CancelablePromise<Players> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/players',
            query: {
                'level': level,
            },
            errors: {
                404: `Players not found`,
            },
        });
    }

    /**
     * Get elo ratings
     * @returns EloRatings Success
     * @throws ApiError
     */
    public getEloRatings({
        level,
    }: {
        /**
         * League level
         */
        level?: string,
    }): CancelablePromise<EloRatings> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/atp-elo',
            query: {
                'level': level,
            },
            errors: {
                404: `EloRatings not found`,
            },
        });
    }

}
