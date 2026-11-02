import {MapController} from "@web_view_leaflet_map/views/leaflet_map/leaflet_map_controller.esm";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {patch} from "@web/core/utils/patch";
import {useSearchBarToggler} from "@web/search/search_bar/search_bar_toggler";

// Odoo 18 views render their own search bar in the layout actions slot
patch(MapController, {
    components: {...MapController.components, SearchBar},
});

patch(MapController.prototype, {
    setup() {
        super.setup(...arguments);
        this.searchBarToggler = useSearchBarToggler();
    },
});
