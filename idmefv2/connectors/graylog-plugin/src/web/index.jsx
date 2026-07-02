import 'webpack-entry';

import { PluginManifest, PluginStore } from 'graylog-web-plugin/plugin';

import packageJson from '../../package.json';
import Idmefv2NotificationForm from './Idmefv2NotificationForm';
import Idmefv2NotificationSummary from './Idmefv2NotificationSummary';

const manifest = new PluginManifest(packageJson, {
  eventNotificationTypes: [
    {
      type: 'idmefv2-alert-notification',
      displayName: 'IDMEFv2 Alert Notification',
      formComponent: Idmefv2NotificationForm,
      summaryComponent: Idmefv2NotificationSummary,
      defaultConfig: {
        type: 'idmefv2-alert-notification',
        url: '',
        organization_name: 'Graylog',
        organization_id: 'graylog',
      },
    },
  ],
});

PluginStore.register(manifest);
