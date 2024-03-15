import "./PlayerList.css";

import {getData} from "common/functions/playerData";
import {useGetPlayers} from "common/functions/playerFetch";
import {EloRatings} from "data/openapi";
import React from "react";
import {useQuery} from "react-query";

export const PlayerList: React.FC = () => {
    //const {data, isLoading, isError} = useGetPlayers();
    const {isLoading, isError, data} = useQuery("eloratings", getData);

    if (isLoading) return <div />;

    if (isError) return <div />;

    return (
        <div className="main">
            <ul className="player-list">
                <li className="player-list-item player-list-item-header">
                    <div>
                        <strong>Player</strong>
                    </div>
                    <div>
                        <strong>Elo</strong>
                    </div>
                    <div>
                        <strong>Date</strong>
                    </div>
                </li>
                {data &&
                    data.data &&
                    data.data.map((player: EloRatings) => (
                        <li key={player.id} className="player-list-item">
                            <div>
                                {player.first_name} {player.last_name}
                            </div>
                            <div>{player.elo}</div>
                            <div>
                                {player.latest_date
                                    ? new Date(player.latest_date).toLocaleDateString("en-US", {
                                          year: "numeric",
                                          month: "long",
                                          day: "numeric",
                                      })
                                    : "Not available"}
                            </div>
                        </li>
                    ))}
            </ul>
        </div>
    );
};
