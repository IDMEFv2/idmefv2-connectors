import React from 'react';

const Idmefv2NotificationSummary = ({ notification }) => {
  const { config } = notification;

  return (
    <dl>
      <dt>HTTP URL</dt>
      <dd>{config.url}</dd>
      <dt>Organization Name</dt>
      <dd>{config.organization_name || 'Graylog'}</dd>
      <dt>Organization ID</dt>
      <dd>{config.organization_id || 'graylog'}</dd>
    </dl>
  );
};

export default Idmefv2NotificationSummary;
