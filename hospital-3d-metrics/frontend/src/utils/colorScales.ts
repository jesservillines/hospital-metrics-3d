// frontend/src/utils/colorScales.ts
import * as d3 from 'd3';

export const getColorScale = (values: number[], colorRange: [string, string] = ['#fff', '#007dc3']) => {
  const scale = d3.scaleLinear()
    .domain([Math.min(...values), Math.max(...values)])
    .range(colorRange as any);

  return scale;
};