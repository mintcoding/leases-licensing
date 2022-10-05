module.exports = {
    APPLICATION_TYPES: {
        REGISTRATION_OF_INTEREST: 'registration_of_interest',
        LEASE_LICENCE: 'lease_licence',
    },
    ROLES: {
        // GROUP_REGISTRATION_OF_INTEREST_ASSESSOR = "registration_of_interest_assessor"
        // GROUP_REGISTRATION_OF_INTEREST_APPROVER = "registration_of_interest_approver"
        // GROUP_LEASE_LICENCE_ASSESSOR = "lease_licence_assessor"
        // GROUP_LEASE_LICENCE_APPROVER = "lease_licence_approver"
        // GROUP_COMPETITIVE_PROCESS_EDITOR = "competitive_process_editor"
        // GROUP_FINANCE = "finance"

        // ASSESSOR: {ID: 'assessor', TEXT: 'Assessor'},
        // APPROVER: {ID: 'approver', TEXT: 'Approver'},
        // REFERRAL: {ID: 'referral', TEXT: 'Referral'},

        REGISTRATION_OF_INTEREST_ASSESSOR: {ID: 'registration_of_interest_assessor', TEXT: 'Registration of Interest Assessor'},
        REGISTRATION_OF_INTEREST_APPROVER: {ID: 'registration_of_interest_approver', TEXT: 'Registration of Interest Approver'},
        LEASE_LICENCE_ASSESSOR: {ID: 'lease_licence_assessor', TEXT: 'Lease Licence Assessor'},
        LEASE_LICENCE_APPROVER: {ID: 'lease_licence_approver', TEXT: 'Lease Licence Approver'},
        COMPETITIVE_PROCESS_EDITOR: {ID: 'competitive_process_editor', TEXT: 'Competitive Process Editor'},
        FINANCE: {ID: 'finance', TEXT: 'Finance'},
        REFERRAL: {ID: 'referral', TEXT: 'Referral'},
    },
    PROPOSAL_STATUS: {
        DRAFT: {ID: 'draft', TEXT: 'Draft'},
        AMENDMENT_REQUIRED: {ID: 'amendment_required', TEXT: 'Amendment Required'},
        WITH_ASSESSOR: {ID: 'with_assessor', TEXT: 'With Assessor'},
        WITH_ASSESSOR_CONDITIONS: {ID: 'with_assessor_conditions', TEXT: 'With Assessor (Conditions)'},
        WITH_APPROVER: {ID: 'with_approver', TEXT: 'With Approver'},
        WITH_REFERRAL: {ID: 'with_referral', TEXT: 'With Referral'},
        WITH_REFERRAL_CONDITIONS: {ID: 'with_referral_conditions', TEXT: 'With Referral (Conditions)'},
        APPROVED_APPLICATION: {ID: 'approved_application', TEXT: 'Approved (Application)'},
        APPROVED_COMPETITIVE_PROCESS: {ID: 'approved_competitive_process', TEXT: 'Approved (Competitive Process)'},
        APPROVED_EDITING_INVOICING: {ID: 'approved_editing_invoicing', TEXT: 'Approved (Editing Invoicing)'},
        APPROVED: {ID: 'approved', TEXT: 'Approved'},
        DECLINED: {ID: 'declined', TEXT: 'Declined'},
        DISCARDED: {ID: 'discarded', TEXT: 'Discarded'},
    },
    COMPETITIVE_PROCESS_STATUS: {
        IN_PROGRESS: {ID: 'in_progress', TEXT: 'In Progress'},
        COMPLETED: {ID: 'completed', TEXT: 'Completed'},
        DISCARDED: {ID: 'discarded', TEXT: 'Discarded'},
    },
    APPROVAL_STATUS: {
        CURRENT: {ID: 'current', TEXT: 'Current'},
        CURRENT_BASE_FEE_REVIEW: {ID: 'current_base_fee_review', TEXT: 'Current (base fee review)'},
        CURRENT_RENEWAL_REVIEW: {ID: 'current_renewal_review', TEXT: 'Current (renewal review)'},
        CANCELLED: {ID: 'cancelled', TEXT: 'Cancelled'},
        SURRENDERED: {ID: 'surrendered', TEXT: 'Surrendered'},
        SUSPENDED: {ID: 'suspended', TEXT: 'Suspended'},
        HOLD_OVER_LEASE_DEED_OF_LICENCE: {ID: 'hold_over_lease_deed_of_licence', TEXT: 'Hold-over (lease, deed of licence)'},
        HOLD_OVER_BASE_FEE_REVIEW: {ID: 'hold_over_base_fee_review', TEXT: 'Hold-over (base fee review)'},
        EXTENDED_LEASE_DEED_OF_LICENCE: {ID: 'extended_lease_deed_of_licence', TEXT: 'Extended (lease, deed of licence)'},
        EXTENDED_BASE_FEE_REVIEW: {ID: 'extended_base_fee_review', TEXT: 'Extended (base fee review)'},
        EXPIRED_LICENCE: {ID: 'expired_licence', TEXT: 'Expired (licence)'},
    },
    DRAFT: 'Draft',
    WITH_ASSESSOR: 'With Assessor',
    WITH_ASSESSOR_CONDITIONS: 'With Assessor (Conditions)',
    WITH_APPROVER: 'With Approver',
    WITH_REFERRAL: 'With Referral',
    WITH_REFERRAL_CONDITIONS: 'With Referral (Conditions)',
    APPROVED_APPLICATION: 'Approved (Application)',
    APPROVED_COMPETITIVE_PROCESS: 'Approved (Competitive Process)',
    APPROVED_EDITING_INVOICING: 'Approved (Editing Invoicing)',
    APPROVED: 'Approved',
    DECLINED: 'Declined',
    DISCARDED: 'Discarded',
};
