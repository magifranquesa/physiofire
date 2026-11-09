# Figure 1: study area (double column).
# Inputs: FirEUrisk fuel fractions at 0.05 deg (data/interim/static/fuel_fireurisk_fine.nc) grouped into the analysis
# classes and dominant class per cell with the same functions as the epoch analysis (R/epoch_lib.R); EFFIS perimeters
# of the 22 selected fires (data/interim/fires/effis_iberia_2018_2026.gpkg, data/fires/selected_fires.csv); burned
# and control cells (data/processed/epoch/epoch_cells.csv); Natural Earth admin-0 1:10m v5.1.1 (public domain;
# data/raw/naturalearth, see docs/data_sources.md) for coastline, borders and the Europe locator.
# (a) Iberian Peninsula: fuel classes, fire perimeters, locator map of Europe and extent of (b);
# (b) north-west: burned cells (0.05 deg outline) and controls, by colour, over the fuel classes and perimeters.
# Geographic coordinates (EPSG:4326), as the 0.05 deg analysis grid. Scale bars computed at the panel's mean latitude.
# Usage (from the repository root): Rscript R/manuscript_figures/fig1_study_area.R

source("R/manuscript_figures/style.R")
source("R/epoch_lib.R")
suppressPackageStartupMessages({ library(sf); library(terra) })
sf_use_s2(FALSE)

FUEL_LAB <- c(closed_forest = "Closed forest", open_forest = "Open forest", shrubland = "Shrubland",
              wet_heath = "Heathland and wetland", grassland = "Grassland", cropland = "Cropland",
              nonfuel = "Non-fuel")
FUEL_COL <- c(`Closed forest` = "#2d6a4f", `Open forest` = "#8fbf88", Shrubland = "#c9a66b",
              `Heathland and wetland` = "#a77ba6", Grassland = "#ece59a", Cropland = "#e6e0d3",
              `Non-fuel` = "#ffffff")
CELL_COL <- c(`Burned cells` = "#D55E00", Controls = "#0072B2")   # Okabe-Ito vermilion and blue

# --- data ---------------------------------------------------------------------------------------------------------
reg <- cfg$region
frac <- vegetation_fractions(cfg, root, "fine", source = "fuel")
dom <- dominant_group(frac)
fuel_df <- as.data.frame(dom, xy = TRUE, na.rm = TRUE) |>
  mutate(fuel = factor(FUEL_LAB[names(frac)[veg]], levels = FUEL_LAB))
ne <- st_read(file.path(root, "data/raw/naturalearth/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"),
              quiet = TRUE) |> st_make_valid()
iberia <- ne |> filter(ADM0_A3 %in% c("ESP", "PRT"))
land <- st_union(iberia)
fuel_sf_mask <- vect(land)
dom_land <- mask(dom, fuel_sf_mask)                            # sea and neighbouring countries out
fuel_df <- as.data.frame(dom_land, xy = TRUE, na.rm = TRUE) |> mutate(x = round(x, 3), y = round(y, 3)) |>
  mutate(fuel = factor(FUEL_LAB[names(frac)[veg]], levels = FUEL_LAB))

fires <- read_csv(file.path(root, "data/fires/selected_fires.csv"), show_col_types = FALSE) |> filter(!exclude)
per <- st_read(file.path(root, "data/interim/fires/effis_iberia_2018_2026.gpkg"), quiet = TRUE) |>
  mutate(id = as.integer(id)) |> filter(id %in% fires$fire_id)
stopifnot(nrow(per) >= nrow(fires), all(fires$fire_id %in% per$id))
cells <- read_csv(file.path(root, "data/processed/epoch/epoch_cells.csv"), show_col_types = FALSE) |>
  filter(fire_id %in% fires$fire_id)
res <- as.numeric(cfg$grids$fine$resolution_deg)
cells_sf <- st_sf(cells |> mutate(kind = ifelse(group == "burned", "Burned cells", "Controls")),
                  geometry = cell_polygons(cells, res))
message(sprintf("%d fires, %d perimeters, %d burned cells, %d controls", nrow(fires), nrow(per),
                sum(cells$group == "burned"), sum(cells$group == "control")))

# --- helpers ------------------------------------------------------------------------------------------------------
scale_bar <- function(x0, y0, km, lat) {
  dl <- km / (111.32 * cos(lat * pi / 180))
  list(annotate("rect", xmin = x0, xmax = x0 + dl / 2, ymin = y0, ymax = y0 + 0.012 * km / 10 * 0 + dl * 0.06,
                fill = "black", colour = "black", linewidth = 0.2),
       annotate("rect", xmin = x0 + dl / 2, xmax = x0 + dl, ymin = y0, ymax = y0 + dl * 0.06,
                fill = "white", colour = "black", linewidth = 0.2),
       annotate("text", x = c(x0, x0 + dl / 2, x0 + dl), y = y0 + dl * 0.06, vjust = -0.5,
                label = c("0", km / 2, sprintf("%d km", km)), size = (BASE_PT - 1) / .pt, family = FONT))
}
map_theme <- theme_ms() + theme(panel.grid.major = element_line(linewidth = 0.15, colour = "grey80"),
                                panel.background = element_rect(fill = "#eef3f7"), axis.title = element_blank())

# extent of (b): fires in the north-west, with a margin
nw <- cells |> group_by(fire_id) |> summarise(lon = mean(lon), lat = mean(lat)) |> filter(lon < -5.5, lat > 40)
bb <- c(xmin = min(cells$lon[cells$fire_id %in% nw$fire_id]) - 0.25,
        xmax = max(cells$lon[cells$fire_id %in% nw$fire_id]) + 0.25,
        ymin = min(cells$lat[cells$fire_id %in% nw$fire_id]) - 0.25,
        ymax = max(cells$lat[cells$fire_id %in% nw$fire_id]) + 0.25)

# --- (a) Iberia ----------------------------------------------------------------------------------------------------
xa <- c(-9.6, 3.4); ya <- c(35.9, 44.0)
pa <- ggplot() +
  geom_sf(data = ne, fill = "grey92", colour = "grey60", linewidth = 0.15) +
  geom_tile(data = fuel_df, aes(x, y, fill = fuel), width = res, height = res) +
  geom_sf(data = iberia, fill = NA, colour = "grey30", linewidth = 0.2) +
  geom_sf(data = per, fill = "black", colour = "black", linewidth = 0.15) +
  annotate("rect", xmin = bb["xmin"], xmax = bb["xmax"], ymin = bb["ymin"], ymax = bb["ymax"], fill = NA,
           colour = "black", linewidth = 0.4) +
  annotate("text", x = bb["xmax"], y = bb["ymax"], label = "(b)", hjust = -0.2, vjust = 1, size = BASE_PT / .pt,
           family = FONT, fontface = "bold") +
  scale_bar(-9.3, 36.1, 200, 36.5) +
  scale_fill_manual(values = FUEL_COL, name = NULL, drop = FALSE) +
  coord_sf(xlim = xa, ylim = ya, expand = FALSE, crs = 4326) + map_theme +
  theme(legend.position = "bottom") +
  guides(fill = guide_legend(nrow = 2, override.aes = list(colour = "grey55", linewidth = 0.2)))

eu_box <- st_as_sfc(st_bbox(c(xmin = xa[1], xmax = xa[2], ymin = ya[1], ymax = ya[2]), crs = 4326))
inset <- ggplot() +
  geom_sf(data = ne, fill = "grey85", colour = "white", linewidth = 0.1) +
  geom_sf(data = iberia, fill = "grey45", colour = "white", linewidth = 0.1) +
  geom_sf(data = eu_box, fill = NA, colour = "black", linewidth = 0.3) +
  coord_sf(xlim = c(-12, 32), ylim = c(34, 62), expand = FALSE, crs = 4326) +
  theme_void() + theme(panel.background = element_rect(fill = "white", colour = "black", linewidth = 0.3))
pa <- pa + inset_element(inset, left = 0.70, bottom = 0.0, right = 1.0, top = 0.36, align_to = "panel")

# --- (b) north-west ------------------------------------------------------------------------------------------------
pb <- ggplot() +
  geom_sf(data = ne, fill = "grey92", colour = "grey60", linewidth = 0.15) +
  geom_tile(data = fuel_df, aes(x, y, fill = fuel), width = res, height = res, alpha = 0.75) +
  geom_sf(data = iberia, fill = NA, colour = "grey30", linewidth = 0.25) +
  geom_sf(data = per, fill = "grey20", colour = "black", alpha = 0.35, linewidth = 0.2) +
  geom_sf(data = cells_sf, aes(colour = kind), fill = NA, linewidth = 0.35) +
  scale_bar(bb[["xmin"]] + 0.1, bb[["ymin"]] + 0.08, 50, mean(bb[c("ymin", "ymax")])) +
  scale_fill_manual(values = FUEL_COL, guide = "none") +
  scale_colour_manual(values = CELL_COL, name = NULL) +
  coord_sf(xlim = bb[c("xmin", "xmax")], ylim = bb[c("ymin", "ymax")], expand = FALSE, crs = 4326) + map_theme +
  theme(legend.position = "bottom") +
  guides(colour = guide_legend(override.aes = list(fill = NA, linewidth = 0.6)))

p <- (pa | pb) + plot_layout(widths = c(1.35, 1)) +
  plot_annotation(tag_levels = list(c("(a)", "", "(b)")))
save_fig(p, "fig1_study_area", WIDTH_DOUBLE, 115)
