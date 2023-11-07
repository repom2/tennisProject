import {createRoute} from "common/functions/routeFunctions";

export const conversationPageTemp = createRoute(() => {
    return `/players` as const;
});
