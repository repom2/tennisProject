/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Bets } from '../models/Bets';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class BetsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Get bets
     * @returns Bets Success
     * @throws ApiError
     */
    public getBets({
        level,
    }: {
        /**
         * Players
         */
        level?: string,
    }): CancelablePromise<Bets> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/bet-list',
            query: {
                'level': level,
            },
            errors: {
                404: `Bet list not found`,
            },
        });
    }

}
