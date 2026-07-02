import React from 'react';
import cloneDeep from 'lodash/cloneDeep';

const Idmefv2NotificationForm = ({ config, validation, onChange }) => {
  const handleChange = (event) => {
    const { name, value } = event.target;
    const nextConfig = cloneDeep(config);
    nextConfig[name] = value;
    onChange(nextConfig);
  };

  const urlError = validation?.errors?.url?.[0];
  const orgNameError = validation?.errors?.organization_name?.[0];
  const orgIdError = validation?.errors?.organization_id?.[0];

  return (
    <>
      <div className={`form-group ${urlError ? 'has-error' : ''}`}>
        <label htmlFor="idmefv2-url" className="control-label">HTTP(S) URL <span className="required-star">*</span></label>
        <input
          id="idmefv2-url"
          name="url"
          type="url"
          className="form-control"
          value={config.url || ''}
          onChange={handleChange}
          placeholder="https://your-siem.example.com/idmefv2/alerts"
          required
        />
        <span className="help-block">{urlError ?? 'The HTTP(S) endpoint that will receive IDMEFv2 JSON messages via POST.'}</span>
      </div>

      <div className={`form-group ${orgNameError ? 'has-error' : ''}`}>
        <label htmlFor="idmefv2-org-name" className="control-label">Organization Name</label>
        <input
          id="idmefv2-org-name"
          name="organization_name"
          type="text"
          className="form-control"
          value={config.organization_name || ''}
          onChange={handleChange}
          placeholder="Graylog"
        />
        <span className="help-block">{orgNameError ?? 'Name of your organization, included in every IDMEFv2 message.'}</span>
      </div>

      <div className={`form-group ${orgIdError ? 'has-error' : ''}`}>
        <label htmlFor="idmefv2-org-id" className="control-label">Organization ID</label>
        <input
          id="idmefv2-org-id"
          name="organization_id"
          type="text"
          className="form-control"
          value={config.organization_id || ''}
          onChange={handleChange}
          placeholder="graylog"
        />
        <span className="help-block">{orgIdError ?? 'Unique identifier for your organization.'}</span>
      </div>
    </>
  );
};

export default Idmefv2NotificationForm;
