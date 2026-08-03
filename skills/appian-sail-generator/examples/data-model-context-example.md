# OTIEC Application Record Type Context Reference

This document provides the specific record type definitions for use when creating SAIL expressions.

<available_record_types>
## Available Record Types - Phase 1

<otiec_app_employment_history>
### OTIEC App Employment History
**Record Type**: `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History'`

**Description**: 
Stores data about App Employment Histories.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| employmentId | Integer | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{d75af521-7600-4e6f-8bf2-d9bbf7cde850}employmentId'` |
| safetyPercentage | Integer | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{9bab4744-0cec-41d7-a850-544adb958004}safetyPercentage'` |
| applicationId | Integer | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{7b512574-cb68-4832-be59-5688e2152212}applicationId'` |
| endDate | Date | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{64715049-8036-4832-87c3-f92d1775d51f}endDate'` |
| employerName | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{99316994-99a8-4c96-85a2-b30846918607}employerName'` |
| contactPerson | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{c3f9c5c1-da03-453e-9808-62538449ea13}contactPerson'` |
| contactPhone | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{48a8b70f-6676-445b-b49e-e378e21ac94f}contactPhone'` |
| contactEmail | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{661c555a-c777-4223-8856-b360763058ce}contactEmail'` |
| employerAddress | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{a4242f5d-c78c-468e-a566-7574a780ff2b}employerAddress'` |
| city | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{f5c3350c-a225-431b-ab08-250e47e084f5}city'` |
| state | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{369619ea-0b95-4d36-894b-8dbeb577484d}state'` |
| startDate | Date | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{b38dc40f-edb6-4899-bd84-6fd6bfd1b9d3}startDate'` |
| zipCode | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{cb6c2372-4e91-4948-8c95-084ecfe1166e}zipCode'` |
| overallJobDuties | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{4f3f370b-b68d-412c-95c3-35f0abe54e8b}overallJobDuties'` |
| safetyResponsibilities | Text | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{b355119f-eeb3-4bb5-982f-35d17fc429dc}safetyResponsibilities'` |
| employmentOrder | Integer | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{d2fb1cca-b040-4b42-921a-caec19e0a979}employmentOrder'` |
| createdBy | User | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{a62a2b70-657b-418e-925b-22ef6b680798}createdBy'` |
| createdOn | Datetime | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{ffdd03b1-cc2d-4412-9e70-acef23f197dc}createdOn'` |
| modifiedBy | User | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{961fe459-d835-4868-90c3-0e6a3861aecc}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{f52edecc-af0e-4fdd-8c82-bccaec79f493}modifiedOn'` |
| isActive | Boolean | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.fields.{ea489ce8-96cf-45de-aa85-0de4ea6de6ad}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| modifiedByUser | many-to-one | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.relationships.{4f9648b4-f04c-4368-976e-c122ad85559f}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.relationships.{dc3410a6-db15-4885-828a-db462e3c0b52}createdByUser'` |
| application | many-to-one | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.relationships.{a65196c8-1fee-4e5b-8325-376d4b8eafb1}application'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{3eb360f5-349c-4b15-bb24-3ca875b72bff}OTIEC App Employment History.filters.{13ea3159-16f7-43a5-94b6-7558686d8f9a}UPV3 Application'` |

**Record Actions**:

Not available

</otiec_app_employment_history>

<otiec_app_education_certification>
### OTIEC App Education Certification
**Record Type**: `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification'`

**Description**: 
Stores data about App Education Certifications.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| educationCertId | Integer | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{63eabcc2-4045-464c-b379-1f537952958c}educationCertId'` |
| institutionName | Text | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{0eaa02aa-3924-4f30-b2d4-2288514a128c}institutionName'` |
| degreeLevel | Text | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{3fcee4dd-91f3-413f-b654-4853c89c0753}degreeLevel'` |
| certificationName | Text | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{64699872-8905-4740-ad65-dee3219b3329}certificationName'` |
| supportingDocument | CollaborationDocument | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{07c16af0-f10a-4fe4-9d0d-13860fff30c3}supportingDocument'` |
| applicationId | Integer | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{2693b44f-51bc-4ac0-8fa1-000108c8eee2}applicationId'` |
| degreeMajor | Text | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{7ffdbb0e-c7f2-4fde-b5ed-d14a88935d93}degreeMajor'` |
| graduationDate | Date | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{ee12b0aa-c9b1-49af-a226-34027d98725c}graduationDate'` |
| educationCertTypeId | Integer | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{45587f44-766b-4fc9-bdb7-17a15d970c2e}educationCertTypeId'` |
| substitutionYears | Integer | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{02e6e2fb-50fe-4354-ba54-cfa5461421eb}substitutionYears'` |
| createdBy | User | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{899f99e3-ef3c-43ae-93d8-5898980073a3}createdBy'` |
| createdOn | Datetime | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{e5fd3052-9d85-4ef9-a28b-5363c970b2d1}createdOn'` |
| modifiedBy | User | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{adf8e46a-580e-49f9-9be0-62c6a1737bd5}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{799bccb0-561c-4dcc-bfc4-10d7e6038a1a}modifiedOn'` |
| isActive | Boolean | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.fields.{54998163-32f6-4fc7-a6df-ffc2e106ed1e}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| documentProperties | many-to-one | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.relationships.{34637525-a131-4465-a6f4-1ab6190f7ba2}documentProperties'` |
| createdByUser | many-to-one | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.relationships.{abb2fcf5-7b80-44a2-9b7a-6041b7d6b87f}createdByUser'` |
| application | many-to-one | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.relationships.{6b7720c9-43e6-4472-8331-0288f98829a2}application'` |
| refEducationCertType | many-to-one | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.relationships.{4d56f66c-3b55-49c3-8131-569f9bf51e39}refEducationCertType'` |
| modifiedByUser | many-to-one | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.relationships.{bc479be9-04ee-4deb-8767-cf9c08d48d01}modifiedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.filters.{ae3f5d21-3627-4074-8d3b-c70f0b1e25b0}UPV3 Application'` |
| UPV3 Ref Education Cert Type | `'recordType!{50dfc70a-5b3f-4562-8dae-37f54cc58e19}OTIEC App Education Certification.filters.{eaa4b58a-2dac-4087-8fc0-b3a31e394d52}UPV3 Ref Education Cert Type'` |

**Record Actions**:

Not available

</otiec_app_education_certification>

<otiec_application_course>
### OTIEC Application Course
**Record Type**: `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course'`

**Description**: 
Stores data about Application Courses.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| applicationCourseId | Integer | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{79cbf3ad-f759-40a0-9497-5e019bd7795b}applicationCourseId'` |
| denialReason | Text | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{9d442f48-beb6-42c8-848c-c29636a24836}denialReason'` |
| courseId | Integer | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{b7490842-24ef-4cec-8181-d238ddc88ff5}courseId'` |
| enroleLink | Text | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{cce4fdb1-6734-4b30-8edc-0607fd1a880e}enroleLink'` |
| applicationId | Integer | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{6af96356-713a-45b2-a5c7-1a5ede416af8}applicationId'` |
| approvalDate | Date | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{0070b45f-a447-46eb-b153-b1cc4367fefd}approvalDate'` |
| prerequisiteVerified | Boolean | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{2842c819-ad60-4afb-9e56-e1ccf8234a16}prerequisiteVerified'` |
| approvalStatusId | Integer | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{c2a70819-383d-4074-8919-844974761ae3}approvalStatusId'` |
| providedRegistrationCode | Text | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{7dcd5691-19b0-44ac-b5ee-53f07df13b81}providedRegistrationCode'` |
| createdBy | User | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{5534a9ba-99d5-483d-be3f-3bcbaf754da6}createdBy'` |
| createdOn | Datetime | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{b7e7193e-3b12-4e6f-ab29-10042b76c86d}createdOn'` |
| modifiedBy | User | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{5deec5ea-1323-45aa-a101-268ee1842644}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{05c0916b-5dff-4a9e-9283-17f59c64262e}modifiedOn'` |
| isActive | Boolean | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.fields.{9799afb8-aa4c-4783-abeb-8503f21ee9c5}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| application | many-to-one | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.relationships.{84dfe0d2-3141-4f53-8662-74a193dcaf7a}application'` |
| course | many-to-one | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.relationships.{727f966f-2eb3-486b-a428-0025a468c3b9}course'` |
| createdByUser | many-to-one | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.relationships.{7eec6ed6-393f-4ca6-9ed2-77eb941a4d91}createdByUser'` |
| modifiedByUser | many-to-one | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.relationships.{3d99aec4-8fa6-48d0-9745-1dc26b0e6f4b}modifiedByUser'` |
| refApprovalStatus | many-to-one | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.relationships.{c3c3a742-375a-4a03-801b-fb139bb668a3}refApprovalStatus'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.filters.{0fa9da76-ea9e-4cbe-85c1-3f55398afac9}UPV3 Application'` |
| UPV3 Course | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.filters.{82aca4c1-b947-47b6-b5b5-ad9ab1f1f9cd}UPV3 Course'` |
| UPV3 Ref Approval Status | `'recordType!{63a3eaab-355d-484e-970e-0e56fe7e323d}OTIEC Application Course.filters.{90a699b9-41a2-4332-827c-6724b716656b}UPV3 Ref Approval Status'` |

**Record Actions**:

Not available

</otiec_application_course>

<otiec_applicant>
### OTIEC Applicant
**Record Type**: `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant'`

**Description**: 
Stores data about Applicants.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| applicantId | Integer | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{b24f70d0-76d3-4595-b993-71e4c4a10fa5}applicantId'` |
| company | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{dc31b2f7-78ca-4bf8-ad13-9a74a49e79d0}company'` |
| firstName | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{e7ab5be0-88d6-464d-a8e8-2b030eb22f7b}firstName'` |
| lastName | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{2a87c5dd-e07d-4456-b531-4451505470b3}lastName'` |
| zipCode | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{8930a8dc-1513-44c0-b8a7-91bd1dd1220f}zipCode'` |
| fax | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{c7ec9361-f955-4cc9-91cb-f8116e74c634}fax'` |
| mailingAddress | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{d0b8b27c-ad68-47b8-a296-9ae46a27a3dc}mailingAddress'` |
| city | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{980d766c-c28e-418a-9ee6-d5fe6a10646c}city'` |
| phone | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{cecfdb08-92ce-41ba-8741-14049e0897a1}phone'` |
| appianUserId | User | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{f9a5874e-01b2-4b80-8230-a2879c4adfac}appianUserId'` |
| jobTitle | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{c4e54e28-b3d2-4a3f-9529-42e301196c3a}jobTitle'` |
| state | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{658acf7c-244f-4cca-a48a-518289d487e0}state'` |
| email | Text | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{d804c6a1-9617-425f-9d7b-097c5717ccb2}email'` |
| createdBy | User | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{fb46590e-2ddc-40df-912d-1a4d6b6b81ff}createdBy'` |
| createdOn | Datetime | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{dc2d8913-289f-44b7-aba5-a2db9e521005}createdOn'` |
| modifiedBy | User | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{ceedb843-6d08-4a94-9ae8-80261a0d54f0}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{1b1e8969-3f87-42ba-8528-8ad881e33a33}modifiedOn'` |
| isActive | Boolean | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{d8f8ccfa-8036-464b-b91c-ba92dde74140}isActive'` |
| applicationId | Integer | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{c3989225-eee6-4655-9c1f-75aea6bb9cd1}applicationId'` |
| prefilledByPreviousData | Boolean | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.fields.{64a2dacb-2deb-4e6d-92ef-dd8870792c93}prefilledByPreviousData'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| modifiedByUser | many-to-one | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.relationships.{1ce24926-89a2-494b-9be6-f458925ed461}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.relationships.{27e0d690-bb15-4bdc-ad18-e35858bb0578}createdByUser'` |
| user | many-to-one | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.relationships.{2b975e69-b899-40bc-8c90-e60a5e7bec8c}user'` |
| application | one-to-one | `'recordType!{94e5db91-03f4-4ce3-986b-412ad7febb03}OTIEC Applicant.relationships.{f8db32c4-92ba-4e0d-9d95-07695db01005}application'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_applicant>

<otiec_application>
### OTIEC Application
**Record Type**: `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application'`

**Description**: 
Stores data about Applications.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| applicationId | Integer | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{568822bd-addf-4021-8f24-f8928a93031a}applicationId'` |
| friendlyId | Text | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{eeef210c-66e2-445b-b32b-4681df231dc5}friendlyId'` |
| versionNumber | Integer | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{004d397d-cf9c-4256-82db-18e8f847cbac}versionNumber'` |
| signedPdfDocument | CollaborationDocument | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{16a0d13f-5649-4a69-9cfc-84452587c745}signedPdfDocument'` |
| previousRevocationFlag | Boolean | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{f0396fc0-4100-4351-8644-5ed43a6af214}previousRevocationFlag'` |
| docusignEnvelopeId | Text | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{9b7871ef-0fff-435f-b147-88329da2bacb}docusignEnvelopeId'` |
| submissionDate | Datetime | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{9ae61958-37fa-4562-b285-b714d974f3a3}submissionDate'` |
| lastModifiedDate | Datetime | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{c0976dcc-b9d0-44a1-ac4c-51436bb7f522}lastModifiedDate'` |
| applicationStatusId | Integer | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{67221500-e03a-4fab-86ac-7f0ed8439589}applicationStatusId'` |
| watchListCheckedDate | Date | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{120f316e-d718-4f85-8130-f02c4de06d93}watchListCheckedDate'` |
| reinstatementLetterAttached | Boolean | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{ae132327-0b5d-4109-982f-b15dbf495175}reinstatementLetterAttached'` |
| createdBy | User | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{c4545096-9068-4b78-9e87-f1a9e89e412e}createdBy'` |
| createdOn | Datetime | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{50088e21-c87e-40c2-b604-0126da6b073f}createdOn'` |
| modifiedBy | User | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{dec7a684-d300-4a23-a1c6-436fc63b4d10}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{fe6fc8bc-dc93-49dd-a807-fbc8a0e9c617}modifiedOn'` |
| isActive | Boolean | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.fields.{d03af000-ea62-43b0-82a5-4f533af969b2}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| comment | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{1d403676-66ed-4f55-b252-651c4e109d14}comment'` |
| appEducationCertification | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{d0fb1483-9ae0-4ef5-b8e4-104a5599aa57}appEducationCertification'` |
| task | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{be8bd8fd-da10-48f7-a9d9-c0539d63f743}task'` |
| supportingDocument | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{082dadfd-254d-4bf8-be7a-d7de29dd2984}supportingDocument'` |
| appEmploymentHistory | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{e9efa783-bc97-4f1e-9ddc-1eea5c003747}appEmploymentHistory'` |
| applicationCourse | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{1efa39a0-b247-4beb-be70-4d99f4059f03}applicationCourse'` |
| refApplicationStatus | many-to-one | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{484a89ee-6f13-47c2-9e4d-1c06904b48fb}refApplicationStatus'` |
| createdByUser | many-to-one | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{e6b94bbd-0235-4e75-989d-268ded2683f5}createdByUser'` |
| documentProperties | many-to-one | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{ed53f008-56c3-4ade-b7f5-7c806cfabf7f}documentProperties'` |
| applicant | one-to-one | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{248d8c76-009f-4608-9914-3364f1f78869}applicant'` |
| modifiedByUser | many-to-one | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{69f7970b-cff0-45d2-aec6-9a8b0149b325}modifiedByUser'` |
| prerequisites | one-to-many | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.relationships.{6b1b823c-3007-4547-ba38-4ee80bdf8ce4}prerequisites'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Applicant | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.filters.{5e0cc9e4-5af2-4d8e-bd1f-de4bacf767c1}UPV3 Applicant'` |
| OTIEC Application Status | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.filters.{95328bb0-848e-4c94-be37-a739ae585516}OTIEC Application Status'` |

**Record Actions**:

| **Action Name** | **Action Reference** |
|----------------|---------------------|
| Update Application | `'recordType!{ea98ca89-4bec-4a83-87eb-7c54f3753ad0}OTIEC Application.actions.{2813fd83-1f6a-44f6-b2dd-4eebd599ed93}updateApplication'` |

</otiec_application>

## Available Record Types - Phase 2

<otiec_external_validation_url>
### OTIEC External Validation Url
**Record Type**: `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url'`

**Description**: 

Stores data about External Validation Urls.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| validationUrlId | Integer | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{45e15c2e-d678-437b-8296-db4eb73ac16f}validationUrlId'` |
| url | Text | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{1855cb53-badb-4cb0-8c74-88b449153c49}url'` |
| urlType | Text | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{eaaeea48-bc73-49d2-9022-e71f1f364dac}urlType'` |
| description | Text | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{0de35a07-4710-404b-a68d-63adee4c33b5}description'` |
| createdBy | User | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{8edd78db-ed9a-4da7-9255-db11aee7be9e}createdBy'` |
| createdOn | Datetime | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{19cb7f5f-267e-4be5-a86d-9e9af84e52f1}createdOn'` |
| modifiedBy | User | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{ee13d5d0-7495-4fa7-88d9-f26b1d11473e}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{1e5a4f40-74b7-4918-b39e-38d057eba7f2}modifiedOn'` |
| isActive | Boolean | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.fields.{647983b2-c7fe-449c-9613-f80402b255a2}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | many-to-one | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.relationships.{596d0222-7cb2-4aec-9365-0a6c2401aa55}createdByUser'` |
| modifiedByUser | many-to-one | `'recordType!{4a53234d-315e-4fd1-a846-ade0068e7c03}OTIEC External Validation Url.relationships.{5ffd6231-16ec-423b-b907-d0f19b0f5cac}modifiedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_external_validation_url>

<otiec_application_prerequisite>
### OTIEC Application Prerequisite
**Record Type**: `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite'`

**Description**: 

The application's prerequisites that must be met

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| applicationPrerequisiteId | Integer | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{f6f0c35d-05a9-4426-b4b6-a7905f02fdda}applicationPrerequisiteId'` |
| applicationId | Integer | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{f08b64ed-9c35-4c67-b4fd-bfc2a2be6318}applicationId'` |
| refPrerequisiteId | Integer | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{c90a521c-ab9c-4d2b-9333-df1b8f04b7a9}refPrerequisiteId'` |
| isSatisfied | Boolean | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{e211a5d5-169b-48b4-ad04-709435e1ad3b}isSatisfied'` |
| createdBy | User | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{0dabe49d-32a4-40e8-8ec9-65a262ec4b48}createdBy'` |
| createdOn | Datetime | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{199be515-097f-4d2a-b277-375037a5b979}createdOn'` |
| modifiedBy | User | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{a76cac65-842c-44b6-9452-ff242c4e4b5b}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.fields.{dc65e6af-c94a-4736-a5da-dc98550ef12e}modifiedOn'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | many-to-one | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.relationships.{e5d93bea-6f5a-4e74-8dde-213fd57500d4}createdByUser'` |
| modifiedByUser | many-to-one | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.relationships.{828820e8-3b93-4d5d-9dd4-d6a1dbd0a448}modifiedByUser'` |
| refCoursePrerequisite | many-to-one | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.relationships.{5c0c1bf2-1c2c-4336-8919-445bbb8c3091}refCoursePrerequisite'` |
| application | many-to-one | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.relationships.{20793037-279e-42b6-80e8-d045e7c352e3}application'` |
| supportingDocument | one-to-many | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.relationships.{28620add-3498-4b46-9368-d02bcd0e2e92}supportingDocument'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| OTIEC Ref Course Prerequisite | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.filters.{371bdef3-628a-47f4-97a6-ddd195700a67}OTIEC Ref Course Prerequisite'` |
| OTIEC Application | `'recordType!{62b5ddf4-fcb9-4a91-81ab-e72488209105}OTIEC Application Prerequisite.filters.{f1a3333f-dac2-4d09-9a0b-70c4131969c1}OTIEC Application'` |

**Record Actions**:

Not available

</otiec_application_prerequisite>

<otiec_comment>
### OTIEC Comment
**Record Type**: `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment'`

**Description**: 

Stores data about Comments.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| commentId | Integer | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{3e1824a2-2b33-45d1-99c2-48fd102433c4}commentId'` |
| applicationId | Integer | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{d59ec510-c5a5-418e-9f1f-02210120cb0c}applicationId'` |
| commentText | Text | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{b361eb18-b444-42d7-8c04-e925641e3d18}commentText'` |
| addedBy | User | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{516f5d86-f5f5-4fd3-a373-4ef8cd248361}addedBy'` |
| addedOn | Datetime | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{8810e9db-f818-4014-ae8b-f9ead2b4e65d}addedOn'` |
| createdBy | User | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{e3bbca30-1cbd-426b-b989-f619838f5efa}createdBy'` |
| createdOn | Datetime | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{17786ed9-d5f6-47a2-b095-360fb45bb7d3}createdOn'` |
| modifiedBy | User | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{c9f14532-802c-40f2-8f88-5f7f414bf6f4}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{0468d135-cb44-4bee-9b31-6485c8decf8f}modifiedOn'` |
| isActive | Boolean | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.fields.{372988f6-750f-423a-8739-9279fb313f6e}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| application | many-to-one | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.relationships.{a9d356ae-9a2a-442c-9658-4c85119f6557}application'` |
| modifiedByUser | many-to-one | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.relationships.{5bf1c1e6-d6bf-4b5d-a42a-80f8a1b3282a}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.relationships.{22bdc357-5204-4bfd-a96d-8988775f07d8}createdByUser'` |
| addedByUser | many-to-one | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.relationships.{9e581016-574f-4ca1-b829-53f1e6cc8920}addedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{760ffc80-1d35-4b7f-9137-b0884ebad9a7}OTIEC Comment.filters.{d74f1b10-b8e9-40e8-9fd2-6bd6fe5de2ce}UPV3 Application'` |

**Record Actions**:

Not available

</otiec_comment>

<otiec_ref_application_status>
### OTIEC Ref Application Status
**Record Type**: `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status'`

**Description**: 

Stores data about Ref Application Statuses.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{dfe492c7-b1ff-42c9-9d34-83d8da11cb87}id'` |
| value | Text | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{7881ac61-54ea-4d92-8de9-df7efad25201}value'` |
| sortOrder | Integer | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{6dbb410d-6210-48e7-a0cf-a363d9040b28}sortOrder'` |
| createdBy | User | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{695c11eb-84cb-47f1-bd42-fe2cb779d499}createdBy'` |
| createdOn | Datetime | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{95d8730c-f5c7-4e90-a54f-ef51ae063d75}createdOn'` |
| modifiedBy | User | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{48b91914-dc2c-4359-9530-7bc3741ff55b}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{0b762e99-ea89-432a-afc0-b38bc0027ebb}modifiedOn'` |
| isActive | Boolean | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.fields.{98941c61-3a0b-4dbc-b0ad-22163a67e35b}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| modifiedByUser | many-to-one | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.relationships.{dc66006e-b295-4fbe-a51c-acb64703848a}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.relationships.{c88b601f-189b-4328-87b1-7d473eeb49e3}createdByUser'` |
| application | one-to-many | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.relationships.{92023363-b1e0-468b-8ddc-891885c01d4d}application'` |
| valueTranslation | many-to-one | `'recordType!{9395f7a1-18a8-44eb-a2ef-45e2a3b27a44}OTIEC Ref Application Status.relationships.{4bdbeea7-f937-41c5-b4b9-a22f3b192fba}valueTranslation'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_application_status>

<otiec_course>
### OTIEC Course
**Record Type**: `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course'`

**Description**: 

Stores data about Courses.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| courseId | Integer | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{980f555c-1b41-442e-8479-a27b7954ae9f}courseId'` |
| endDate | Date | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{093e7f6f-3c46-4305-be93-f7d07ddca89e}endDate'` |
| courseName | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{7a471995-26bc-4aa5-a95a-9af17fdaea89}courseName'` |
| courseNumber | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{d3749e4a-26f5-4dae-8d4c-29c0a319fb82}courseNumber'` |
| courseSessionId | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{ed7d88c2-00d8-45d9-9f62-77c025910c48}courseSessionId'` |
| startDate | Date | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{5097bfbc-1142-4ef3-b0c4-35a02caaca6d}startDate'` |
| enroleCourseId | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{957638a8-4422-47fe-9983-aea967579e51}enroleCourseId'` |
| maxEnrollment | Integer | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{7a2196c8-782e-4489-8a75-6c0e86d03f0d}maxEnrollment'` |
| courseTypeId | Integer | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{7206dbb1-dda1-4f64-b4e1-895c3121772b}courseTypeId'` |
| location | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{157395eb-8230-450f-8b5d-9073b91dccad}location'` |
| registrationCode | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{8a6ef513-90e2-469a-ab3a-81641fbd1a0d}registrationCode'` |
| description | Text | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{2f5950af-6dec-4aab-8760-e252f3e48c75}description'` |
| isContractCourse | Boolean | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{ae12784a-0830-4aae-992f-70ea4c1ddfb3}isContractCourse'` |
| createdBy | User | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{113dd0b9-6a17-415f-87f7-55aac523d36f}createdBy'` |
| createdOn | Datetime | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{ec340e19-be49-4952-8b09-92ae0fdb2775}createdOn'` |
| modifiedBy | User | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{f0a04384-d449-4006-98c0-3e52e054ea47}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{0b248f10-128b-4fb8-9fed-a7c6f138d5b9}modifiedOn'` |
| isActive | Boolean | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.fields.{14fbb16e-eff1-455a-a7a0-340f481e977d}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| refCourseType | many-to-one | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.relationships.{89eaed4a-99ed-4153-ac4f-a4abec116795}refCourseType'` |
| modifiedByUser | many-to-one | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.relationships.{67972283-f408-4f6c-b43b-76fdb7ae0020}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.relationships.{e614b034-a1d7-4b1d-ab25-50bc51ca8722}createdByUser'` |
| applicationCourse | one-to-many | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.relationships.{6b2bd89a-4f64-436b-9a3f-0dfdb3688f54}applicationCourse'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| OTIEC Course Type | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.filters.{451c4d20-e68d-4c87-9393-9301c5b86b42}OTIEC Course Type'` |
| OTIEC Course Name | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.filters.{556ed1f7-a340-472c-9ffb-c50186ad930d}OTIEC Course Name'` |
| Course Session | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.filters.{17f83652-0461-4d02-aadb-0263c7e7ff59}Course Session'` |

**Record Actions**:

| **Action Name** | **Action Reference** |
|----------------|---------------------|
| Update Course | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.actions.{429cb3d0-7b68-4458-8eaf-2f8c328aa7e9}Update Course'` |
| Quick Apply | `'recordType!{e5a90da5-9ad3-45c1-b9b2-ea78c3f502da}OTIEC Course.actions.{6ec20998-0721-441d-8b10-46428b7dd11d}Quick Apply'` |

</otiec_course>

## Available Record Types - Phase 3

<otiec_ref_course_type>
### OTIEC Ref Course Type
**Record Type**: `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type'`

**Description**: 

Stores data about Ref Course Types.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{fd285f58-7b2f-4c7b-ae60-22946cc99f46}id'` |
| courseNumber | Text | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{8be6f5b5-9d1a-48c9-b756-51ce9ace418c}courseNumber'` |
| areaOfExpertise | Text | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{c8eb6554-7c1c-46fa-b433-01d9642f359f}areaOfExpertise'` |
| value | Text | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{de8741bf-8ecc-4433-ba4a-3a386355b414}value'` |
| requiresPrerequisites | Boolean | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{17d682da-a7cf-44da-8574-2193e513ea9e}requiresPrerequisites'` |
| sortOrder | Integer | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{a5eaa9b7-7add-4a87-8aaa-0e3eafb813e5}sortOrder'` |
| createdBy | User | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{57ff5379-9876-40fb-b562-a2564b7780bf}createdBy'` |
| createdOn | Datetime | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{77f0a30a-adbc-4c56-b918-6e528f04c8dc}createdOn'` |
| modifiedBy | User | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{06cdb836-5463-4d60-a50b-c0cc5cf51b66}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{99297f51-0e89-4761-9040-94b6c55542ab}modifiedOn'` |
| isActive | Boolean | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.fields.{5365cf29-76c0-445e-840b-13fe5b67341c}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| modifiedByUser | MANY_TO_ONE | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.relationships.{c72a42a2-111a-458d-9e43-c9229590ef57}modifiedByUser'` |
| course | ONE_TO_MANY | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.relationships.{bffee9ad-1b6a-4f76-b09a-f9500fadb15b}course'` |
| createdByUser | MANY_TO_ONE | `'recordType!{7feb10ed-0315-4ac6-a7a8-b4808f5c6ca8}OTIEC Ref Course Type.relationships.{e4b125c0-adfc-49a5-996a-e2dde261f160}createdByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_course_type>

<otiec_ref_course_prerequisite>
### OTIEC Ref Course Prerequisite
**Record Type**: `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite'`

**Description**: 

For courses in the OSHA app, there are pre-reqs necessary 

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| coursePrerequisiteId | Integer | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{fe307bad-736a-4a50-9354-f70004a0c5c7}coursePrerequisiteId'` |
| courseTypeId | Integer | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{eeccea71-8d10-44d9-904f-b5d1731c5443}courseTypeId'` |
| prerequisiteCourse | Integer | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{2f727433-838e-47c6-854c-d05431874e43}prerequisiteCourse'` |
| createdBy | User | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{8a6b72d4-8fc7-46de-86d4-614d5c1ecbd3}createdBy'` |
| createdOn | Datetime | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{9b0e48f3-1772-463c-9c53-42dc41bcd058}createdOn'` |
| modifiedBy | User | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{06e54fa7-a778-4562-9be1-ab66e4aa3c3b}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.fields.{e6420e4a-02d3-46b8-a468-22c69a21df1b}modifiedOn'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | MANY_TO_ONE | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.relationships.{e0098cdc-6a39-47e3-9a26-04f05449eecc}createdByUser'` |
| modifiedByUser | MANY_TO_ONE | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.relationships.{155f66aa-aab4-4cea-a425-a93e8c02899c}modifiedByUser'` |
| courseType | MANY_TO_ONE | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.relationships.{f7b6559e-1999-42ea-a7fd-846764d197bb}courseType'` |
| prerequisiteCourseType | MANY_TO_ONE | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.relationships.{bfd223eb-716f-45f6-a4b3-370bcb99d536}prerequisiteCourseType'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| OTIEC Ref Course Type | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.filters.{105c4f10-dae0-41b9-af2b-70efb48f9ea2}OTIEC Ref Course Type'` |
| OTIEC Ref Course Type | `'recordType!{a01c45f7-fa15-4468-8f77-caad4ea9afd6}OTIEC Ref Course Prerequisite.filters.{ae78f29a-948a-4047-97fa-4857b76ee303}OTIEC Ref Course Type'` |

**Record Actions**:

Not available

</otiec_ref_course_prerequisite>

<otiec_ref_approval_status>
### OTIEC Ref Approval Status
**Record Type**: `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status'`

**Description**: 

Stores data about Ref Approval Statuses.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{7291435a-803f-4e44-b2c4-31afbd45d25e}id'` |
| value | Text | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{4c95567c-6ee7-48b4-8ecd-c39e3c8a7004}value'` |
| sortOrder | Integer | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{da85618e-4518-41b4-9684-b2e304e99f3c}sortOrder'` |
| createdBy | User | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{5a4bd8dd-caee-444e-8a32-e1956db9661c}createdBy'` |
| createdOn | Datetime | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{6221a44d-6e3c-4fe8-9a14-0bf17afcf88e}createdOn'` |
| modifiedBy | User | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{6305d735-6d47-408e-a2f1-d4021f76f760}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{fd7a64cd-19e6-486b-b935-98f8acf09e7a}modifiedOn'` |
| isActive | Boolean | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.fields.{abb9158c-1428-4bda-98d5-9dc5f7bfeacb}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| applicationCourse | ONE_TO_MANY | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.relationships.{822e6255-cdfc-4b0a-b0bd-c562bc035c75}applicationCourse'` |
| modifiedByUser | MANY_TO_ONE | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.relationships.{c9d75ee9-20f0-4362-a8bd-97b517f25ac0}modifiedByUser'` |
| createdByUser | MANY_TO_ONE | `'recordType!{ec27730e-12e3-4a92-88e5-ce377ccaea1f}OTIEC Ref Approval Status.relationships.{da110bfc-375d-4b12-b4a8-d8605df0f167}createdByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_approval_status>

<otiec_ref_document_type>
### OTIEC Ref Document Type
**Record Type**: `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type'`

**Description**: 

Stores data about Ref Document Types.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{411b8f62-cf68-4670-ba0e-f995af769080}id'` |
| value | Text | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{9d9091ef-28e1-4a05-ace8-9d9268807ec5}value'` |
| requiredForApplication | Boolean | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{39363f5b-f89b-493e-80e9-2bd4d538d18e}requiredForApplication'` |
| sortOrder | Integer | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{9338fdb1-1817-41a6-b476-49073c3d2977}sortOrder'` |
| createdBy | User | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{436971a7-6170-4fd4-9958-aba196d0855c}createdBy'` |
| createdOn | Datetime | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{ae0cc20a-8b55-4263-9097-9fd27ec21f6f}createdOn'` |
| modifiedBy | User | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{ecffdb51-7591-420b-96f3-b6390b6273e6}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{03eb98e2-c786-4f3c-a628-4f94f213db8c}modifiedOn'` |
| isActive | Boolean | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.fields.{5bcb400a-ff89-4a6a-a253-023849d98fcb}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| supportingDocument | ONE_TO_MANY | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.relationships.{55519633-ee33-4d99-9027-7d0f8d8e8a9d}supportingDocument'` |
| modifiedByUser | MANY_TO_ONE | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.relationships.{1535b966-751d-4fe1-b671-6f3149ba1473}modifiedByUser'` |
| createdByUser | MANY_TO_ONE | `'recordType!{f46d0345-d6a9-4636-b6ac-ce918e3be06b}OTIEC Ref Document Type.relationships.{00759a5d-fc27-44e3-a82f-a7ffc88d584a}createdByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_document_type>

<otiec_ref_course_prerequisite_document>
### OTIEC Ref Course Prerequisite Document
**Record Type**: `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document'`

**Description**: 



**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| coursePrerequisiteDocumentId | Integer | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{c64d35fa-1122-4e3e-aec1-4400a9bddd57}coursePrerequisiteDocumentId'` |
| coursePrerequisiteId | Integer | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{5663ee1c-333a-4f60-bac5-882e53220989}coursePrerequisiteId'` |
| documentTypeId | Integer | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{646ecc98-06fe-4af2-8cd8-f7045c5a1eb9}documentTypeId'` |
| createdBy | User | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{3ddde032-cacf-42e2-9e3d-0edb7dbf0b3e}createdBy'` |
| createdOn | Datetime | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{7bbd600c-7c69-4cda-82e8-f6e063b6a745}createdOn'` |
| modifiedBy | User | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{d2b992f1-58b8-4418-b1d1-4e9c19fc84e9}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.fields.{b1cd48bb-2d07-4ab6-ae88-b9a7d524b529}modifiedOn'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | MANY_TO_ONE | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.relationships.{bd8f1d02-f3f7-4826-8e55-95e5ce78c50b}createdByUser'` |
| modifiedByUser | MANY_TO_ONE | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.relationships.{a9d0edf1-58df-42ab-90ee-cfa9b1fbb099}modifiedByUser'` |
| refCoursePrerequisite | MANY_TO_ONE | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.relationships.{aa7705f2-d353-49ef-81d3-93f008ef8ce5}refCoursePrerequisite'` |
| refDocumentType | MANY_TO_ONE | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.relationships.{f4fcfc37-83ca-4e26-b087-f77dd9c0e997}refDocumentType'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| OTIEC Ref Course Prerequisite | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.filters.{5a2d4683-e3ba-4de3-b13f-7982a6a317cf}OTIEC Ref Course Prerequisite'` |
| OTIEC Ref Document Type | `'recordType!{f6780d9d-7e0b-4287-b85a-e2e2b448f7b4}OTIEC Ref Course Prerequisite Document.filters.{498876a7-cfe6-4bed-a39b-b9c393391249}OTIEC Ref Document Type'` |

**Record Actions**:

Not available

</otiec_ref_course_prerequisite_document>

## Available Record Types - Phase 4

<!-- BEGIN RECORD TYPE TEMPLATE - REPEAT FOR EACH RECORD TYPE -->

<otiec_supporting_document>
### OTIEC Supporting Document
**Record Type**: `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document'`

**Description**: 

Stores data about Supporting Documents.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| documentId | Integer | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{d4b07a8d-c286-410d-a22a-eb8c00c656f2}documentId'` |
| documentFile | CollaborationDocument | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{13bb4220-4a1c-4944-b4cd-9c4da121cd48}documentFile'` |
| documentName | Text | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{ac52deb3-2d11-4255-aed4-9fadc49a89fa}documentName'` |
| applicationId | Integer | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{34c57bed-4d16-4f2f-b01d-c3ac07bed110}applicationId'` |
| applicationPrerequsiteId | Integer | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{83b58890-1cb6-47d2-95d5-4f8e5917746e}applicationPrerequsiteId'` |
| uploadDate | Date | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{6089b51b-4b33-48c0-bd3e-7fad365de1af}uploadDate'` |
| documentTypeId | Integer | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{0f2c0ebc-b556-474f-a002-031f60cfd58d}documentTypeId'` |
| fileSize | Integer | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{9baed879-c659-4675-afda-e112519e7d84}fileSize'` |
| uploadedByApplicant | Boolean | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{27fba708-d8d9-43db-9f8e-f2453dd01158}uploadedByApplicant'` |
| createdBy | User | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{7ec0bc60-1944-4868-a835-f27c1b434133}createdBy'` |
| createdOn | Datetime | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{d2a20c51-a0b9-408a-9e10-ae10f29c7387}createdOn'` |
| modifiedBy | User | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{89ad4767-d5f1-400d-8d97-7c21dec0a80c}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{97f512fa-b1f9-4e6f-ada0-63fff06a5adf}modifiedOn'` |
| isActive | Boolean | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.fields.{02ef3122-b19b-47a0-98b4-7848233cc015}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| refDocumentType | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{2eaa4957-b25d-45cb-a242-a9e6370999dd}refDocumentType'` |
| documentProperties | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{4e275e7d-64c1-44c4-931d-c8d67672a3d8}documentProperties'` |
| application | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{1a1bf7eb-0c63-4422-bfe0-2a6ab7771dee}application'` |
| modifiedByUser | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{08d73d4e-5349-4b27-99e0-3c01d79b6aab}modifiedByUser'` |
| createdByUser | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{4efa5b96-c8c7-4172-9ccb-929d2b3be693}createdByUser'` |
| applicationPrerequisite | many-to-one | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.relationships.{4459c01a-c6eb-415d-bcc7-dfaa57e99f0d}applicationPrerequisite'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.filters.{b6d69494-2e28-47a9-a10e-60b04c13db34}UPV3 Application'` |
| UPV3 Ref Document Type | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.filters.{5ff1cfb3-8231-4650-b687-19115b7a13db}UPV3 Ref Document Type'` |
| OTIEC Application Prerequisite | `'recordType!{0f01d755-e563-43f2-96bb-a717374ae5ce}OTIEC Supporting Document.filters.{ea2295fb-e36f-409d-bdef-5d8ac0f0692a}OTIEC Application Prerequisite'` |

**Record Actions**:

Not available

</otiec_supporting_document>

<otiec_ref_education_cert_type>
### OTIEC Ref Education Cert Type
**Record Type**: `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type'`

**Description**: 

Stores data about Ref Education Cert Types.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{fd97ce6b-6399-4b40-be52-b4dfdbb389fa}id'` |
| value | Text | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{9e0e3f80-3dde-4e63-9056-4cfc7fd9dddc}value'` |
| substitutionYears | Integer | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{3130a39d-f569-4f1e-a34d-33485ba36bb9}substitutionYears'` |
| sortOrder | Integer | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{6dd56a1b-a840-450d-bbc7-fb0b722ff4d4}sortOrder'` |
| createdBy | User | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{51623eff-c7d1-4572-ae65-88bd1e63055e}createdBy'` |
| createdOn | Datetime | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{065b24d3-70e1-4975-8ed7-375629e75525}createdOn'` |
| modifiedBy | User | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{35451a75-4ef6-4c2e-9f09-84ba06b18349}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{2c9c2958-3c3d-4b82-888d-5fb111dda8eb}modifiedOn'` |
| isActive | Boolean | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.fields.{5838b3e7-518c-400d-957d-d7d3e621ee81}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| appEducationCertification | one-to-many | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.relationships.{2222ab17-bf33-4105-9e20-88408851451a}appEducationCertification'` |
| createdByUser | many-to-one | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.relationships.{14e442c8-23dc-4b19-8c66-49fe1168ace0}createdByUser'` |
| modifiedByUser | many-to-one | `'recordType!{4feb6a14-0ffd-4a7c-ac79-7cb49345dc77}OTIEC Ref Education Cert Type.relationships.{fa5c8603-8fe2-40d0-b172-2ad61f551267}modifiedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_education_cert_type>

<otiec_task>
### OTIEC Task
**Record Type**: `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task'`

**Description**: 

Stores data about Tasks.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| taskId | Integer | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{c0b9cc0c-3f98-4234-af8a-4003870613d2}taskId'` |
| assignedTo | User | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{d1fb1484-c33f-40cb-b90e-5a0b3008d3a6}assignedTo'` |
| notes | Text | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{65772eec-fb8f-4915-a559-7d23833cacb0}notes'` |
| completedDate | Datetime | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{c0282a0c-9fff-455d-b5af-985331eb1b90}completedDate'` |
| dueDate | Datetime | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{846e3de0-c9f2-4d83-9c03-5f6a285478c1}dueDate'` |
| createdDate | Datetime | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{3e228089-ef7a-4611-8b82-0ec032d5710d}createdDate'` |
| applicationId | Integer | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{130bb80e-c9c9-4100-bad8-c50907776374}applicationId'` |
| taskStatusId | Integer | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{07855915-eab1-4cf1-affd-74561f777fda}taskStatusId'` |
| taskTypeId | Integer | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{9d7cdba9-13e8-4d65-b37a-872c3823b326}taskTypeId'` |
| createdBy | User | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{bc855108-a109-4f08-8863-f59ec770a375}createdBy'` |
| createdOn | Datetime | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{8a5bb23b-4f4d-4aa9-967b-0029d61835e6}createdOn'` |
| modifiedBy | User | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{c27df219-dbd6-4602-922a-93f46c86eb85}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{8cf50976-a177-4c74-a9b0-b2c7581e1892}modifiedOn'` |
| isActive | Boolean | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.fields.{52cd644e-2c2a-4c53-8118-df1513f1a96e}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| refTaskStatus | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{39599382-7ebf-41b6-8612-5d781a468cfa}refTaskStatus'` |
| createdByUser | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{fe1a8628-244e-42ca-84c0-ea0ca43d3a29}createdByUser'` |
| application | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{489ef079-93a8-42c4-a183-66f4e88685a5}application'` |
| assignedToUser | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{cbbdd022-ae2c-4aa8-86a5-181e90816cd0}assignedToUser'` |
| modifiedByUser | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{40c8d58e-b883-4bb7-8119-63cd3ebbdb39}modifiedByUser'` |
| refTaskType | many-to-one | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.relationships.{8682ef6a-e7fe-4d30-9362-45e47250ccf9}refTaskType'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

| **User Filter Name** | **User Filter Reference** |
|---------------------|---------------------------|
| UPV3 Application | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.filters.{21636cf7-122a-45e5-a95f-e969cdc2e8ee}UPV3 Application'` |
| UPV3 Ref Task Status | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.filters.{fc7466ad-cf2a-4531-ba09-8368acfba1c3}UPV3 Ref Task Status'` |
| UPV3 Ref Task Type | `'recordType!{9de9cd9e-bdde-45ad-b9fd-14c9780ef04d}OTIEC Task.filters.{72dac46f-b539-4acc-a496-f1e910aab647}UPV3 Ref Task Type'` |

**Record Actions**:

Not available

</otiec_task>

<otiec_ref_task_status>
### OTIEC Ref Task Status
**Record Type**: `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status'`

**Description**: 

Stores data about Ref Task Statuses.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{6bf4bfc8-e0ae-403b-ab4b-905908b23779}id'` |
| value | Text | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{0c510bb5-1b8f-410b-8a86-197a2dcff570}value'` |
| sortOrder | Integer | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{f254d86d-5bd9-497a-bf19-41628c36667d}sortOrder'` |
| createdBy | User | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{81ad7c45-7dbe-4a33-bc07-bbca2a3ea249}createdBy'` |
| createdOn | Datetime | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{f09e053a-c82b-4489-99ce-2f6dd8c4143e}createdOn'` |
| modifiedBy | User | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{f97fde85-6ff9-4b8c-9931-78223091606a}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{c8cfc4db-361d-4c5f-8bcc-8a6bb53c48ff}modifiedOn'` |
| isActive | Boolean | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.fields.{40afb684-a93f-4abf-bbba-980ff907972e}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | many-to-one | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.relationships.{c04e1dd6-7fdc-457f-baf3-a5e1fdb5927e}createdByUser'` |
| task | one-to-many | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.relationships.{fc6d58ce-9a96-4d19-89a0-1c4e7656dbec}task'` |
| modifiedByUser | many-to-one | `'recordType!{42fa9d15-be31-47b5-bef6-2be68d747988}OTIEC Ref Task Status.relationships.{8eac1a15-9c5a-4e5e-a738-24dab39766ab}modifiedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_task_status>

<otiec_watch_list_entry>
### OTIEC Watch List Entry
**Record Type**: `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry'`

**Description**: 

Stores data about Watch List Entries.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| watchListId | Integer | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{cecb585a-f1f7-490c-99d4-8d06a36e413b}watchListId'` |
| dateAdded | Date | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{36b9ad8d-1bad-43a7-95e6-9cdf393e36ec}dateAdded'` |
| importBatchDate | Date | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{49badeb8-72f0-4974-9fb5-f698853726dd}importBatchDate'` |
| importFile | CollaborationDocument | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{3e37c639-12d2-4dff-9677-7088e88353f0}importFile'` |
| reason | Text | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{09b99420-c300-482e-9c8e-50bcc439c561}reason'` |
| firstName | Text | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{14a7c4a3-2565-4330-8386-a8dd816e5281}firstName'` |
| lastName | Text | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{116879d3-1eef-4e43-b797-13669c44c79e}lastName'` |
| otiec | Text | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{604c2678-e3cf-43a0-a0d7-6ab9d7ed2a2d}otiec'` |
| correctiveAction | Text | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{e0f0128a-d345-4ddf-a275-1dab50c754d2}correctiveAction'` |
| createdBy | User | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{6838027a-de22-4987-8742-ee662ba1a254}createdBy'` |
| createdOn | Datetime | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{6f98a1d9-8d05-4c19-a603-cff278b09f15}createdOn'` |
| modifiedBy | User | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{019e377c-83fc-4461-8e23-a05d2a021216}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{d4df2ec8-34f0-425a-b5c7-8ce9b369fa5c}modifiedOn'` |
| isActive | Boolean | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.fields.{3c0ca85e-4e32-4eee-a343-6e48eba4de54}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | many-to-one | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.relationships.{1c127da0-8733-461d-80ca-78d3c66f1df2}createdByUser'` |
| modifiedByUser | many-to-one | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.relationships.{4c105a73-c706-47b8-a8d2-3ba714c9ef41}modifiedByUser'` |
| documentProperties | many-to-one | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.relationships.{be655f90-98c5-4a42-904c-e6319e10d8d5}documentProperties'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

| **Action Name** | **Action Reference** |
|----------------|---------------------|
| Update Watch List Entry | `'recordType!{42796f87-b7f8-450e-b2fa-f6a7321e769d}OTIEC Watch List Entry.actions.{0295d2b9-2f02-4acc-ae97-fc106e7a6cb2}updateWatchListEntry'` |

</otiec_watch_list_entry>

<otiec_ref_task_type>
### OTIEC Ref Task Type
**Record Type**: `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type'`

**Description**: 

Stores data about Ref Task Types.

**Fields**:

| **Field Name** | **Data Type** | **Field Reference** |
|----------------|---------------|---------------------|
| id | Integer | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{81a8caf3-0184-458d-b559-210b399de317}id'` |
| value | Text | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{cb6de602-aec9-4a0a-87f4-7cd3efdfd56c}value'` |
| sortOrder | Integer | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{5580798c-f6ee-41fc-9092-f8b70ab42299}sortOrder'` |
| createdBy | User | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{55c7825b-c44e-4255-9d7a-9e7463402571}createdBy'` |
| createdOn | Datetime | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{ac34d885-0e20-4a75-963a-df41cb902128}createdOn'` |
| modifiedBy | User | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{d8bade8e-4bf0-4b52-8670-3953e050be88}modifiedBy'` |
| modifiedOn | Datetime | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{70ce6970-9884-4f37-816c-8c931f127e7b}modifiedOn'` |
| isActive | Boolean | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.fields.{7fb418f9-06b4-4833-8400-464fbc7ce062}isActive'` |

**Relationships**:

| **Relationship Name** | **Type** | **Relationship Reference** |
|----------------------|----------|---------------------------|
| createdByUser | many-to-one | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.relationships.{82189483-31c9-4fd2-8851-ac515bc6c8ef}createdByUser'` |
| task | one-to-many | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.relationships.{713e5860-9d0b-459a-aa29-638a3097b60c}task'` |
| modifiedByUser | many-to-one | `'recordType!{0441114f-42c3-43d3-a759-55fd5dac8fc1}OTIEC Ref Task Type.relationships.{7a9580ba-df1d-4aaa-a633-ee280220cc61}modifiedByUser'` |

**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`

**User Filters**:

Not available

**Record Actions**:

Not available

</otiec_ref_task_type>

</available_record_types>

