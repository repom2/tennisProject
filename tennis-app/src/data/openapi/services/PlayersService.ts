/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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
         * Players
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
                404: `Team not found`,
            },
        });
    }

}
