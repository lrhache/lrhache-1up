from schema import BaseModel


class Patient(BaseModel):
    index = ['name.given', 'name.family']

    def get_fullname(self) -> str:
        name = [n for n in self.data['name'] if n['use'] == 'official'][0]

        return f"{' '.join(name['given'])} {name['family']}"


class Encounter(BaseModel):
    references = [
        'subject', 'participant.individual',
        'serviceProvider', 'location.location']


class Group(BaseModel):
    # This is the only model that references a one to many (Group->members)
    # Also, Group is not referenced in any other model
    # I will omit this model for this exercise since it's behaving differently

    # references = ['member.entity']
    pass


class Organization(BaseModel):
    pass


class AllergyIntolerance(BaseModel):
    references = ['patient']


class CarePlan(BaseModel):
    references = ['encounter', 'subject',
                  'careTeam', 'addresses', 'activity.detail.location']


class CareTeam(BaseModel):
    references = ['encounter', 'subject',
                  'participant.role.member', 'managingOrganization']


class Claim(BaseModel):
    references = ['patient', 'provider', 'prescription', 'item.encounter']


class Condition(BaseModel):
    references = ['encounter', 'subject']


class Device(BaseModel):
    references = ['patient']


class DiagnosticReport(BaseModel):
    references = ['encounter', 'subject', 'performer']


class DocumentReference(BaseModel):
    references = ['subject', 'custodian', 'author', 'content.context']


class ExplanationOfBenefit(BaseModel):
    references = ['patient', 'provider', 'facility',
                  'careTeam.provider', 'claim', 'item.encounter',
                  'contained.subject', 'contained.requester',
                  'contained.performer', 'contained.beneficiary']


class ImagingStudy(BaseModel):
    references = ['encounter', 'subject', 'location']


class Immunization(BaseModel):
    references = ['encounter', 'patient', 'location']


class Location(BaseModel):
    references = ['managingOrganization']


class Medication(BaseModel):
    pass


class MedicationAdministration(BaseModel):
    references = ['subject', 'context']


class MedicationRequest(BaseModel):
    references = ['encounter', 'subject', 'requester', 'reasonReference']


class Observation(BaseModel):
    references = ['encounter', 'subject']


class Practitioner(BaseModel):
    index = ['name.given', 'name.family']

    def get_fullname(self) -> str:
        name = self.data['name'][0]

        return f"{' '.join(name['given'])} {name['family']}"


class PractitionerRole(BaseModel):
    references = ['organization', 'practitioner', 'location']


class Procedure(BaseModel):
    references = ['encounter', 'subject', 'location']


class Provenance(BaseModel):
    references = ['target', 'agent.who', 'agent.onBehalfOf']


class SupplyDelivery(BaseModel):
    references = ['patient']
