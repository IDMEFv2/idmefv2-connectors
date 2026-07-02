/*
 * Copyright (C) 2020 Graylog, Inc.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the Server Side Public License, version 1,
 * as published by MongoDB, Inc.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * Server Side Public License for more details.
 *
 * You should have received a copy of the Server Side Public License
 * along with this program. If not, see
 * <http://www.mongodb.com/licensing/server-side-public-license>.
 */
package org.idmefv2;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonTypeName;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.google.auto.value.AutoValue;
import org.graylog.events.contentpack.entities.EventNotificationConfigEntity;
import org.graylog.events.event.EventDto;
import org.graylog.events.notifications.EventNotificationConfig;
import org.graylog.events.notifications.EventNotificationExecutionJob;
import org.graylog.scheduler.JobTriggerData;
import org.graylog2.contentpacks.EntityDescriptorIds;
import org.graylog2.plugin.rest.ValidationResult;

@AutoValue
@JsonTypeName(Idmefv2AlertNotificationConfig.TYPE_NAME)
@JsonDeserialize(builder = Idmefv2AlertNotificationConfig.Builder.class)
public abstract class Idmefv2AlertNotificationConfig implements EventNotificationConfig {
    public static final String TYPE_NAME = "idmefv2-alert-notification";

    static final String FIELD_URL = "url";
    static final String FIELD_ORGANIZATION_NAME = "organization_name";
    static final String FIELD_ORGANIZATION_ID = "organization_id";

    @JsonProperty(FIELD_URL)
    public abstract String url();

    @JsonProperty(FIELD_ORGANIZATION_NAME)
    public abstract String organizationName();

    @JsonProperty(FIELD_ORGANIZATION_ID)
    public abstract String organizationId();

    public static Builder builder() {
        return Builder.create();
    }

    public abstract Builder toBuilder();

    @Override
    @JsonIgnore
    public JobTriggerData toJobTriggerData(EventDto dto) {
        return EventNotificationExecutionJob.Data.builder().eventDto(dto).build();
    }

    @Override
    @JsonIgnore
    public ValidationResult validate() {
        final ValidationResult result = new ValidationResult();
        if (url() == null || url().trim().isEmpty()) {
            result.addError(FIELD_URL, "HTTP URL cannot be empty.");
        } else {
            try {
                java.net.URI.create(url());
            } catch (Exception e) {
                result.addError(FIELD_URL, "Invalid HTTP URL: " + url());
            }
        }
        return result;
    }

    @Override
    public EventNotificationConfigEntity toContentPackEntity(EntityDescriptorIds entityDescriptorIds) {
        throw new UnsupportedOperationException("IDMEFv2 notification does not support content packs yet.");
    }

    @AutoValue.Builder
    public abstract static class Builder implements EventNotificationConfig.Builder<Builder> {
        @JsonCreator
        public static Builder create() {
            return new AutoValue_Idmefv2AlertNotificationConfig.Builder()
                    .type(TYPE_NAME)
                    .organizationName("Graylog")
                    .organizationId("graylog");
        }

        @JsonProperty(FIELD_URL)
        public abstract Builder url(String url);

        @JsonProperty(FIELD_ORGANIZATION_NAME)
        public abstract Builder organizationName(String name);

        @JsonProperty(FIELD_ORGANIZATION_ID)
        public abstract Builder organizationId(String id);

        public abstract Idmefv2AlertNotificationConfig build();
    }
}
