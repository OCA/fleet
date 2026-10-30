/* global L, setTimeout */
import {MapRenderer} from "@web_view_leaflet_map/views/leaflet_map/leaflet_map_renderer.esm";
import {_t} from "@web/core/l10n/translation";
import {onWillUpdateProps} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

const ROUTE_MAPS = {
    "fleet.telemetry": {
        dateField: "fix_time",
        dayField: "route_day",
        colorField: "route_color",
        vehicleField: "vehicle_id",
        legendTitle: _t("Telemetry Routes"),
    },
    "fsm.order.traccar.route.point": {
        dateField: "fix_time",
        dayField: "route_day",
        colorField: "route_color",
        vehicleField: "vehicle_id",
        legendTitle: _t("Routes"),
    },
    "fsm.order.telemetry.route.point": {
        dateField: "fix_time",
        dayField: "route_day",
        colorField: "route_color",
        vehicleField: "vehicle_id",
        legendTitle: _t("Routes"),
    },
};

patch(MapRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.fleetTelemetryRouteLayers = [];
        this.fleetTelemetryRouteLegend = null;
        onWillUpdateProps(async (nextProps) => {
            if (this.isFleetTelemetryRouteMap(nextProps)) {
                await this.loadFleetTelemetryRouteRecords(nextProps);
                setTimeout(() => this.drawFleetTelemetryRoutes(nextProps), 0);
            } else {
                this.clearFleetTelemetryRoutes();
            }
        });
    },

    isFleetTelemetryRouteMap(props = this.props) {
        return Boolean(ROUTE_MAPS[props.resModel]);
    },

    getFleetTelemetryRouteConfig(props = this.props) {
        return ROUTE_MAPS[props.resModel];
    },

    async loadRecords() {
        if (!this.isFleetTelemetryRouteMap()) {
            return super.loadRecords(...arguments);
        }
        await this.loadFleetTelemetryRouteRecords(this.props);
    },

    async loadFleetTelemetryRouteRecords(props) {
        const config = this.getFleetTelemetryRouteConfig(props);
        const fields = Array.from(
            new Set([
                ...this.getFields(),
                config.dateField,
                config.dayField,
                config.colorField,
                config.vehicleField,
            ])
        );
        this.records = await this.orm.searchRead(
            props.resModel,
            props.domain || [],
            fields,
            {
                limit: props.limit || 5000,
                context: props.context || {},
            }
        );
    },

    clearFleetTelemetryRoutes() {
        if (!this.leafletMap) {
            return;
        }
        for (const layer of this.fleetTelemetryRouteLayers || []) {
            this.leafletMap.removeLayer(layer);
        }
        this.fleetTelemetryRouteLayers = [];
        if (this.fleetTelemetryRouteLegend) {
            this.leafletMap.removeControl(this.fleetTelemetryRouteLegend);
            this.fleetTelemetryRouteLegend = null;
        }
    },

    drawFleetTelemetryRoutes(props = this.props) {
        if (
            !this.leafletMap ||
            !this.records?.length ||
            !L ||
            !this.isFleetTelemetryRouteMap(props)
        ) {
            return;
        }
        this.clearFleetTelemetryRoutes();

        const config = this.getFleetTelemetryRouteConfig(props);
        const latitudeField = this.fieldLatitude;
        const longitudeField = this.fieldLongitude;
        const routesByVehicleDay = new Map();
        for (const record of this.records) {
            const lat = record[latitudeField];
            const lng = record[longitudeField];
            if (!lat || !lng) {
                continue;
            }
            const vehicle = record[config.vehicleField];
            const vehicleKey = Array.isArray(vehicle)
                ? String(vehicle[0])
                : "no_vehicle";
            const vehicleName = Array.isArray(vehicle) ? vehicle[1] : _t("No Vehicle");
            const day = record[config.dayField] || _t("No Date");
            const groupKey = `${vehicleKey}|${day}`;
            if (!routesByVehicleDay.has(groupKey)) {
                routesByVehicleDay.set(groupKey, {
                    vehicleKey,
                    vehicleName,
                    day,
                    records: [],
                });
            }
            routesByVehicleDay.get(groupKey).records.push(record);
        }

        const bounds = [];
        const legendItems = [];
        for (const group of routesByVehicleDay.values()) {
            const records = group.records;
            records.sort((first, second) =>
                String(first[config.dateField] || "").localeCompare(
                    String(second[config.dateField] || "")
                )
            );
            const coordinates = records.map((record) => [
                record[latitudeField],
                record[longitudeField],
            ]);
            if (coordinates.length < 2) {
                continue;
            }
            bounds.push(...coordinates);
            const color = records[0][config.colorField] || "#017e84";
            const layer = L.polyline(coordinates, {
                color,
                weight: 4,
                opacity: 0.85,
            }).addTo(this.leafletMap);
            this.fleetTelemetryRouteLayers.push(layer);
            legendItems.push({
                vehicleKey: group.vehicleKey,
                vehicleName: group.vehicleName,
                day: group.day,
                color,
                layer,
            });
        }
        this.addFleetTelemetryRouteLegend(legendItems, config.legendTitle);
        if (bounds.length) {
            this.leafletMap.fitBounds(bounds, {padding: [30, 30]});
        }
    },

    addFleetTelemetryRouteLegend(items, title) {
        if (!items.length) {
            return;
        }
        const legend = L.control({position: "topright"});
        legend.onAdd = () => {
            const container = L.DomUtil.create("div", "o_fleet_telemetry_route_legend");
            container.style.background = "white";
            container.style.padding = "8px 10px";
            container.style.border = "1px solid #d8dadd";
            container.style.borderRadius = "6px";
            container.style.boxShadow = "0 1px 4px rgba(0,0,0,.2)";
            container.style.maxHeight = "260px";
            container.style.overflowY = "auto";
            container.innerHTML = `<strong>${title}</strong>`;
            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.disableScrollPropagation(container);

            const selectedVehicles = new Map();
            const selectedDays = new Map();
            for (const item of items) {
                selectedVehicles.set(item.vehicleKey, true);
                selectedDays.set(item.day, true);
            }

            const updateVisibility = () => {
                for (const item of items) {
                    const visible =
                        selectedVehicles.get(item.vehicleKey) &&
                        selectedDays.get(item.day);
                    if (visible && !this.leafletMap.hasLayer(item.layer)) {
                        item.layer.addTo(this.leafletMap);
                    } else if (!visible && this.leafletMap.hasLayer(item.layer)) {
                        this.leafletMap.removeLayer(item.layer);
                    }
                }
            };

            const addSectionTitle = (text) => {
                const titleRow = L.DomUtil.create("div", "", container);
                titleRow.style.fontWeight = "600";
                titleRow.style.marginTop = "8px";
                titleRow.textContent = text;
            };

            const addCheckbox = (label, checked, onChange, colorValue = false) => {
                const row = L.DomUtil.create("label", "", container);
                row.style.display = "flex";
                row.style.alignItems = "center";
                row.style.gap = "6px";
                row.style.margin = "4px 0 0";
                const checkbox = L.DomUtil.create("input", "", row);
                checkbox.type = "checkbox";
                checkbox.checked = checked;
                if (colorValue) {
                    const color = L.DomUtil.create("span", "", row);
                    color.style.display = "inline-block";
                    color.style.width = "18px";
                    color.style.height = "4px";
                    color.style.background = colorValue;
                }
                const text = L.DomUtil.create("span", "", row);
                text.textContent = label;
                checkbox.addEventListener("change", () => onChange(checkbox.checked));
            };

            const vehicles = Array.from(
                new Map(
                    items.map((item) => [item.vehicleKey, item.vehicleName])
                ).entries()
            ).sort((first, second) => first[1].localeCompare(second[1]));
            addSectionTitle(_t("Vehicles"));
            for (const [vehicleKey, vehicleName] of vehicles) {
                addCheckbox(vehicleName, true, (checked) => {
                    selectedVehicles.set(vehicleKey, checked);
                    updateVisibility();
                });
            }

            const days = Array.from(
                new Map(items.map((item) => [item.day, item.color])).entries()
            ).sort((first, second) =>
                String(first[0]).localeCompare(String(second[0]))
            );
            addSectionTitle(_t("Route Days"));
            for (const [day, color] of days) {
                addCheckbox(
                    day,
                    true,
                    (checked) => {
                        selectedDays.set(day, checked);
                        updateVisibility();
                    },
                    color
                );
            }
            return container;
        };
        legend.addTo(this.leafletMap);
        this.fleetTelemetryRouteLegend = legend;
    },

    renderMarkers() {
        super.renderMarkers(...arguments);
        if (this.isFleetTelemetryRouteMap()) {
            setTimeout(() => this.drawFleetTelemetryRoutes(), 0);
        }
    },
});
