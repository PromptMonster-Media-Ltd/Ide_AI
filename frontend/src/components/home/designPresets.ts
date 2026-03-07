/**
 * Design Scheme Presets -- Predefined configurations that auto-fill
 * platform, complexity, audience, and tone fields on the Home page.
 * @module components/home/designPresets
 */

export interface DesignPresetDefaults {
  platform: string
  complexity: string
  audience: string
  tone: string
}

export interface DesignPreset {
  id: string
  name: string
  icon: string
  description: string
  defaults: DesignPresetDefaults
}

export const DESIGN_PRESETS: DesignPreset[] = [
  {
    id: 'mobile-app',
    name: 'Mobile App',
    icon: '\u{1F4F1}',
    description: 'iOS/Android native or cross-platform mobile application',
    defaults: { platform: 'Mobile', complexity: 'medium', audience: 'consumers', tone: 'casual' },
  },
  {
    id: 'web-app',
    name: 'Web App',
    icon: '\u{1F310}',
    description: 'Full-stack web application with modern UI',
    defaults: { platform: 'Web', complexity: 'medium', audience: 'consumers', tone: 'casual' },
  },
  {
    id: 'desktop-app',
    name: 'Desktop App',
    icon: '\u{1F5A5}\uFE0F',
    description: 'Native desktop application for Windows, Mac, or Linux',
    defaults: { platform: 'Desktop', complexity: 'complex', audience: 'businesses', tone: 'formal' },
  },
  {
    id: 'data-builder',
    name: 'Data Builder',
    icon: '\u{1F527}',
    description: 'Data pipeline, ETL tool, or analytics dashboard',
    defaults: { platform: 'Web', complexity: 'complex', audience: 'developers', tone: 'technical' },
  },
  {
    id: 'browser-extension',
    name: 'Browser Extension',
    icon: '\u{1F9E9}',
    description: 'Chrome/Firefox browser extension or add-on',
    defaults: { platform: 'Browser Extension', complexity: 'simple', audience: 'consumers', tone: 'casual' },
  },
  {
    id: 'social-app',
    name: 'Social App',
    icon: '\u{1F4AC}',
    description: 'Social network, community, or messaging platform',
    defaults: { platform: 'Mobile', complexity: 'complex', audience: 'consumers', tone: 'startup' },
  },
  {
    id: 'dev-framework',
    name: 'Dev Framework',
    icon: '\u26A1',
    description: 'Developer tool, SDK, API, or open-source framework',
    defaults: { platform: 'Custom', complexity: 'complex', audience: 'developers', tone: 'technical' },
  },
  {
    id: 'vst-plugin',
    name: 'VST/VSTi Plug-in',
    icon: '\uD83C\uDFDB\uFE0F',
    description: 'Audio effect or instrument plug-in for DAWs (VST3/AU/AAX)',
    defaults: { platform: 'Desktop', complexity: 'complex', audience: 'consumers', tone: 'technical' },
  },
]
