import {SearchModel} from "@web/search/search_model";
import {patch} from "@web/core/utils/patch";

const PERIOD_FILTER_PREFIX = "telemetry_period_";

function isPeriodFilter(searchItem) {
    return (
        searchItem.type === "filter" &&
        (searchItem.name || "").startsWith(PERIOD_FILTER_PREFIX)
    );
}

// Telemetry period filters are exclusive: choosing one drops the others
patch(SearchModel.prototype, {
    toggleSearchItem(searchItemId) {
        const searchItem = this.searchItems[searchItemId];
        const isActive = this.query.some(
            (queryElem) => queryElem.searchItemId === searchItemId
        );
        if (isPeriodFilter(searchItem) && !isActive) {
            this.query = this.query.filter((queryElem) => {
                const item = this.searchItems[queryElem.searchItemId];
                return !(isPeriodFilter(item) && item.groupId === searchItem.groupId);
            });
        }
        return super.toggleSearchItem(...arguments);
    },
});
