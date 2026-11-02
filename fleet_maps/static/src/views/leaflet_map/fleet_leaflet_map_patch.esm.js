import {MapRenderer} from "@web_view_leaflet_map/views/leaflet_map/leaflet_map_renderer.esm";
import {onWillUpdateProps} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

const leafletMapView = registry.category("views").get("leaflet_map");
if (leafletMapView) {
    leafletMapView.searchMenuTypes = ["filter", "groupBy", "favorite"];
}

patch(MapRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        onWillUpdateProps(async (nextProps) => {
            if (nextProps.resModel !== "fleet.vehicle") {
                return;
            }
            await this.loadFleetRecords(nextProps);
        });
    },

    async loadRecords() {
        if (this.props.resModel !== "fleet.vehicle") {
            return super.loadRecords(...arguments);
        }
        await this.loadFleetRecords(this.props);
    },

    async loadFleetRecords(props) {
        const fields = this.getFields();
        this.records = await this.orm.searchRead(
            this.resModel,
            props.domain || [],
            fields,
            {
                limit: props.limit || 1000,
                context: props.context || {},
            }
        );
    },
});
