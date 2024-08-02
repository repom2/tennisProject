import React from "react";
import {PlayerStatistics} from "data/openapi";

const transformMatchesToJSONString = (matches: any) => {
    return JSON.stringify(matches);
};

const PlayerStats = (data: any) => {
    if (!data) {
        return <p>No data available</p>;
    }

    const {playerSPW, playerRPW, playerMatches, matches} = data.data.data;
    console.log("matches", matches);
    console.log("data", data);

    const matchesJsonString = transformMatchesToJSONString(matches);

    return (
        <div>
            <h3>Player Statistics</h3>
            <p>Serve Points Won (SPW): {playerSPW}</p>
            <p>Return Points Won (RPW): {playerRPW}</p>
            <p>Dominance Ratio (DR): {Math.round((playerSPW / (1-playerRPW)) * 100) / 100}</p>
            <p>Matches Played: {playerMatches}</p>
            <h4>Match Details</h4>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Surface</th>
                        <th>Round Name</th>
                        <th>Tournament Name</th>
                        <th>Opponent</th>
                        <th>SPW</th>
                        <th>RPW</th>
                        <th>DR</th>
                        <th>Hard</th>
                        <th>Clay</th>
                    </tr>
                </thead>
                <tbody>
                    {matches.date.map((date: string, index: number) => (
                        <tr key={index}>
                            <td>{date}</td>
                            <td>{matches.surface[index]}</td>
                            <td>{matches.round_name[index]}</td>
                            <td>{matches.tourney_name[index]}</td>
                            <td>{matches.opponent_name[index]}</td>
                            <td>{matches.spw[index]}</td>
                            <td>{matches.rpw[index]}</td>
                            <td>{matches.dr[index]}</td>
                            <td>{matches.opponent_hard[index]}</td>
                            <td>{matches.opponent_clay[index]}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default PlayerStats;
