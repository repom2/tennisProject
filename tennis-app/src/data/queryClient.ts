import {QueryClient} from "react-query";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
            cacheTime: 60 * 5 * 1000, // clear cache after 5 minutes
            staleTime: 60 * 5 * 1000, // clear cache after 5 minutes
        },
    },
});

export default queryClient;
